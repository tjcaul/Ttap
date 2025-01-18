import pyttsx3
import multiprocess
import queue

def speech_digester_loop(sayQ):
    engine = pyttsx3.init()
    engine.setProperty('rate',500)
    engine.startLoop(False)
    ended=True

    def on_end(name, completed):
        nonlocal ended
        ended=True

    engine.connect('finished-utterance', on_end)
    local_queue = []
    while True:
        next_utterance = None
        try:
            next_utterance=sayQ.get(False)
        except queue.Empty:
            pass

        if next_utterance:
            local_queue.append(next_utterance)

        if (len(local_queue)) and ended:
            if local_queue[0] == "terminate":
                break
            ended=not local_queue[0][1] # if we must wait for end then set ended to false
            engine.stop()
            engine.say(local_queue[0][0]) # unfortunately this is blocking on windows
            local_queue.pop(0)
        engine.iterate()
    # clean up
    engine.endLoop()

sayQ=None
def output_text(text,waitFinish=False):
    global sayQ
    print (text)
    sayQ.put((text,waitFinish))

def all_text_complete():
    global sayQ
    sayQ.put("terminate")

def start_engine():
    global sayQ
    multiprocess.freeze_support()
    sayQ = multiprocess.Queue()
    speech_thread = multiprocess.Process(target=speech_digester_loop,args=(sayQ,))
    speech_thread.start()

if __name__=="__main__":
    start_engine()
    output_text("hello world", True)
    output_text("i bet you just copied the code and ran it", True)
    output_text("anyways, the wait for finish doesnt work", True)
    output_text("maybe you can split the string into words before putting it on the queue", True)
    output_text("at least its non blocking", True)
    output_text("good luck", True)
    all_text_complete()
