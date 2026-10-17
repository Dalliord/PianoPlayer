#Requires AutoHotkey v2.0
#NoTrayIcon
#SingleInstance Off
#Include %A_ScriptDir%\..\ahk\input_utils.ahk
#Include %A_ScriptDir%\..\ahk\plan_reader.ahk

; A pure reader test: neither the worker loop nor PressGroup is called.
global Output := FileOpen("*", "w", "UTF-8-RAW")
global KeyEmitter := ForbidInput
context := "initialization"
try {
    manifest := FileOpen(A_Args[1], "r", "UTF-8")
    count := 0
    while !manifest.AtEOF {
        fields := StrSplit(manifest.ReadLine(), "`t")
        context := fields[1]
        rejected := false
        try {
            plan := ReadPlaybackPlan(fields[2])
        } catch {
            rejected := true
        }
        if fields[3] = "INVALID" {
            if !rejected
                throw Error("invalid plan was accepted")
        } else {
            if rejected
                throw Error("valid plan was rejected")
            if plan.version != Integer(fields[3])
                throw Error("wrong plan version")
            expected := StrSplit(fields[4], ",")
            if plan.events.Length != expected.Length
                throw Error("wrong event count")
            for index, hold in expected {
                if Abs(plan.events[index].hold - Float(hold)) > 0.0001
                    throw Error("wrong per-event hold")
            }
        }
        count += 1
    }
    manifest.Close()
    Output.Write("OK`tplan reader`t" count " plans`n")
    Output.Read(0)
    ExitApp(0)
} catch as err {
    Output.Write("ERROR`t" context ": " err.Message "`n")
    Output.Read(0)
    ExitApp(1)
}

ForbidInput(*) {
    throw Error("reader test attempted keyboard input")
}
