#Requires AutoHotkey v2.0
#SingleInstance Off
#NoTrayIcon
#Include input_utils.ahk
#Include plan_reader.ahk

SetKeyDelay(-1, -1)
SetStoreCapsLockMode(false)
global Output := FileOpen("*", "w", "UTF-8-RAW")
global InputHandle := DllCall("GetStdHandle", "Int", -10, "Ptr")
global InputBuffer := ""
global State := "IDLE"
global Plan := []
global Cursor := 1
global Duration := 0.0
global Hold := 35
global Origin := 0.0
global PausedElapsed := 0.0
global PausedKeys := Map()
global LastProgress := -100.0
global TimerActive := false
global SendMethod := A_Args.Length >= 1 ? A_Args[1] : "Event"
global Frequency := 0
DllCall("QueryPerformanceFrequency", "Int64*", &Frequency)
OnExit(Cleanup)

try {
    Hotkey(A_Args.Length >= 2 ? A_Args[2] : "F6", Toggle)
    Hotkey(A_Args.Length >= 3 ? A_Args[3] : "F7", StopHotkey)
    Hotkey(A_Args.Length >= 4 ? A_Args[4] : "F8", EmergencyHotkey)
    Emit("READY")
    loop {
        Critical("On")
        try {
            ReadCommands()
            Tick()
        } catch as err {
            StopPlayback("ERROR")
            Emit("ERROR`t" StrReplace(StrReplace(err.Message, "`n", " "), "`r", " ") " (line " err.Line ", " err.What ")")
        }
        Critical("Off")
        ; Sleep via Win32 for 1 ms; Sleep(-1) dispatches queued hotkeys promptly.
        DllCall("Sleep", "UInt", State = "PLAYING" ? 1 : 5)
        Sleep(-1)
    }
} catch as err {
    ReleaseAllKeys()
    Emit("ERROR`t" err.Message)
    ExitApp(1)
}

Now() {
    global Frequency
    counter := 0
    DllCall("QueryPerformanceCounter", "Int64*", &counter)
    return counter * 1000.0 / Frequency
}

Emit(message) {
    global Output
    Output.Write(message "`n")
    Output.Read(0)
}

SetState(newState) {
    global State
    State := newState
    Emit("STATE`t" newState)
}

SetResolution(enabled) {
    global TimerActive
    if enabled && !TimerActive {
        if DllCall("winmm\timeBeginPeriod", "UInt", 1) = 0
            TimerActive := true
    } else if !enabled && TimerActive {
        DllCall("winmm\timeEndPeriod", "UInt", 1)
        TimerActive := false
    }
}

ReadCommands() {
    global InputHandle, InputBuffer
    available := 0
    if !DllCall("PeekNamedPipe", "Ptr", InputHandle, "Ptr", 0, "UInt", 0,
                "Ptr", 0, "UInt*", &available, "Ptr", 0) {
        ; Parent exited or closed the pipe: never leave the player running.
        ExitApp()
    }
    if available {
        data := Buffer(Min(available, 65536) + 1, 0)
        count := 0
        if !DllCall("ReadFile", "Ptr", InputHandle, "Ptr", data, "UInt", data.Size - 1,
                    "UInt*", &count, "Ptr", 0)
            ExitApp()
        InputBuffer .= StrGet(data, count, "UTF-8")
    }
    while position := InStr(InputBuffer, "`n") {
        command := Trim(SubStr(InputBuffer, 1, position - 1), "`r")
        InputBuffer := SubStr(InputBuffer, position + 1)
        HandleCommand(command)
    }
}

HandleCommand(command) {
    fields := StrSplit(command, "`t")
    switch fields[1] {
        case "PLAY": LoadPlan(fields[2])
        case "PAUSE": PausePlayback()
        case "RESUME": ResumePlayback()
        case "STOP", "EMERGENCY": StopPlayback()
        case "EXIT": ExitApp()
        default: throw Error("Unknown worker command")
    }
}

LoadPlan(path) {
    global Plan, Cursor, Duration, Hold, Origin, LastProgress, PausedKeys
    ReleaseAllKeys()
    PausedKeys := Map()
    SetResolution(false)
    Plan := []
    loaded := ReadPlaybackPlan(path)
    Hold := loaded.hold
    Duration := loaded.duration
    Plan := loaded.events
    Cursor := 1
    LastProgress := -100.0
    Origin := Now()
    SetResolution(true)
    SetState("PLAYING")
}

Tick() {
    global State, Origin, Plan, Cursor, Duration, Hold, LastProgress
    if State != "PLAYING"
        return
    timestamp := Now()
    elapsed := timestamp - Origin
    ReleaseDue(timestamp)
    ; At most one event per tick: delayed OS scheduling cannot create a burst of stale notes.
    if Cursor <= Plan.Length && Plan[Cursor].offset <= elapsed {
        event := Plan[Cursor]
        if event.kind != "PAUSE" {
            PressGroup(event.keys, timestamp + event.hold)
        }
        Cursor += 1
    }
    if elapsed - LastProgress >= 40 {
        Emit("PROGRESS`t" (Cursor - 1) "`t" Plan.Length "`t" Min(elapsed, Duration))
        LastProgress := elapsed
    }
    if Cursor > Plan.Length && elapsed >= Duration && HeldKeys.Count = 0 {
        Emit("PROGRESS`t" Plan.Length "`t" Plan.Length "`t" Duration)
        StopPlayback("FINISHED")
    }
}

PausePlayback(newState := "PAUSED") {
    global State, Origin, PausedElapsed, PausedKeys
    if State != "PLAYING"
        return
    timestamp := Now()
    PausedElapsed := timestamp - Origin
    PausedKeys := SnapshotHeldKeys(timestamp)
    ReleaseAllKeys()
    SetResolution(false)
    SetState(newState)
}

ResumePlayback() {
    global State, Origin, PausedElapsed, PausedKeys
    if State != "PAUSED"
        return
    timestamp := Now()
    Origin := timestamp - PausedElapsed
    SetResolution(true)
    RestoreHeldKeys(PausedKeys, timestamp)
    PausedKeys := Map()
    SetState("PLAYING")
}

StopPlayback(newState := "STOPPED") {
    global Cursor, Plan, PausedKeys
    ReleaseAllKeys()
    PausedKeys := Map()
    SetResolution(false)
    Cursor := 1
    Plan := []
    SetState(newState)
}

Toggle(*) {
    global State
    if State = "PLAYING"
        PausePlayback()
    else if State = "PAUSED"
        ResumePlayback()
    else
        Emit("HOTKEY`tTOGGLE")
}

StopHotkey(*) {
    StopPlayback()
    Emit("HOTKEY`tSTOP")
}

EmergencyHotkey(*) {
    StopPlayback()
    Emit("HOTKEY`tEMERGENCY")
}

Cleanup(*) {
    ReleaseAllKeys()
    SetResolution(false)
}
