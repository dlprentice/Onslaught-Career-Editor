// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// Parity tests for <see cref="RetailEventScheduler"/> against
/// <c>references/Onslaught/eventmanager.cpp</c> and the pristine
/// <c>74154bfa…</c> bytes at <c>0x0044B2A0</c>, <c>0x0044B2D0</c>,
/// <c>0x0044B310</c>, <c>0x0044B370</c>, <c>0x0044B5C0</c> and
/// <c>0x0044B640</c>.
/// </summary>
public sealed class RetailEventSchedulerTests
{
    private const int Listener = 1;
    private const int SecondListener = 2;

    // Pins: mTime = (float)(mFrameCount * CLOCK_TICK) with a SINGLE rounding to
    // float, from the fild/fmul/fstp at 0x0044B5E4-0x0044B5F0 and CLOCK_TICK
    // 0x3D4CCCCD at 0x005D8578. Frame 1 is the load-bearing case: 0.05f is not
    // representable, so a scheduler that accumulated +0.05f per frame instead
    // of multiplying would agree here and drift later, which frames 3 and 121
    // catch. Does NOT pin what a real frame count reaches, nor the x87
    // precision control - below 2^24 the exact product fits a 53-bit
    // significand, so the control cannot matter for any of these.
    [Theory]
    [InlineData(1u, 0x3D4CCCCDu)]
    [InlineData(2u, 0x3DCCCCCDu)]
    [InlineData(3u, 0x3E19999Au)]
    [InlineData(20u, 0x3F800000u)]
    [InlineData(120u, 0x40C00000u)]
    [InlineData(121u, 0x40C1999Au)]
    [InlineData(20_000u, 0x447A0000u)]
    public void AdvanceTime_ClockIsFrameCountTimesClockTickToTheBit(
        uint frames, uint expectedTimeBits)
    {
        var scheduler = new RetailEventScheduler();
        for (uint frame = 0; frame < frames; frame++)
        {
            scheduler.AdvanceTime();
        }

        Assert.Equal(frames, scheduler.FrameCount);
        Assert.Equal(
            expectedTimeBits, BitConverter.SingleToUInt32Bits(scheduler.Time));
    }

    // Pins the ring rotation and the ready-slot handoff at 0x0044B5CD-0x0044B5F3:
    // mReadyToFlushBuffer takes the OLD mCurrentBufferNum, then the current slot
    // advances modulo 200. Reversing those two lines, or rotating by anything
    // other than NUM_EVENT_LIST_BUFFERS, fails. Does not pin what Flush then
    // does with the ready slot.
    [Fact]
    public void AdvanceTime_HandsOffTheOldSlotThenRotatesModuloTwoHundred()
    {
        var scheduler = new RetailEventScheduler();
        Assert.Equal(0, scheduler.CurrentBufferNum);

        scheduler.AdvanceTime();
        Assert.Equal(0, scheduler.ReadyToFlushBuffer);
        Assert.Equal(1, scheduler.CurrentBufferNum);

        for (int frame = 1; frame < RetailEventScheduler.EventListBuffers; frame++)
        {
            scheduler.AdvanceTime();
        }

        Assert.Equal(
            RetailEventScheduler.EventListBuffers - 1, scheduler.ReadyToFlushBuffer);
        Assert.Equal(0, scheduler.CurrentBufferNum);
    }

    // Pins the whole routing decision of 0x0044B370 at mTime = 0, slot 0:
    // the inclusive 0.051f window (eventmanager.cpp:186 / 0x005DB294), the
    // floor((time - mTime - 0.001f) * 20) bucket (:209-212), the >= 198
    // overflow threshold (cmp ecx, 0xC6 at 0x0044B42D), and the STRICT
    // > 1000000.0f drop (:202) - note 1000000.0f itself is still accepted, into
    // overflow. Each row would fail under an off-by-one threshold, a
    // round-instead-of-floor, or a non-strict ceiling. Does not pin behaviour at
    // a non-zero mTime; that is the wrap test below.
    [Theory]
    [InlineData(0.05f, RetailEventPlacement.ImmediateBucket, 0)]
    [InlineData(0.051f, RetailEventPlacement.ImmediateBucket, 0)]
    [InlineData(0.0510001f, RetailEventPlacement.DelayedBucket, 1)]
    [InlineData(0.06f, RetailEventPlacement.DelayedBucket, 1)]
    [InlineData(0.1f, RetailEventPlacement.DelayedBucket, 1)]
    [InlineData(9.9f, RetailEventPlacement.DelayedBucket, 197)]
    [InlineData(9.9005f, RetailEventPlacement.DelayedBucket, 197)]
    [InlineData(9.95f, RetailEventPlacement.Overflow, -1)]
    [InlineData(1_000_000.0f, RetailEventPlacement.Overflow, -1)]
    [InlineData(1_000_001.0f, RetailEventPlacement.RejectedTooFarAhead, -1)]
    public void AddEvent_RoutesEachReleasedArmToItsExactBucket(
        float time, RetailEventPlacement expected, int expectedBuffer)
    {
        var scheduler = new RetailEventScheduler();
        RetailEventAdmission admission = scheduler.AddEvent(7, Listener, time);

        Assert.Equal(expected, admission.Placement);
        Assert.Equal(expectedBuffer, admission.BufferIndex);
    }

    // Pins NEXT_FRAME (eventmanager.h:14). A negative time takes the immediate
    // arm and its due time is REWRITTEN to mTime + 0.0001f, rounded through a
    // float store (fstp dword at 0x0044B3DF, 0.0001f at 0x005D8570) - not left
    // at -1.0f, and not set to mTime. Both bit patterns would change if the
    // constant, the rounding, or the arm order moved. Does not pin that any
    // released caller passes a negative other than NEXT_FRAME.
    [Fact]
    public void AddEvent_NextFrameStoresMTimePlusOneTenthMilliAsFloat()
    {
        var scheduler = new RetailEventScheduler();

        RetailEventAdmission atZero = scheduler.AddEvent(
            2000, Listener, RetailEventScheduler.NextFrame, RetailEventPriority.EndOfFrame);
        Assert.Equal(RetailEventPlacement.ImmediateBucket, atZero.Placement);
        Assert.Equal(0x38D1B717u, atZero.DueTimeBits);

        scheduler.AdvanceTime();
        RetailEventAdmission atFrameOne = scheduler.AddEvent(
            2000, Listener, RetailEventScheduler.NextFrame, RetailEventPriority.EndOfFrame);
        Assert.Equal(0x3D4D35A9u, atFrameOne.DueTimeBits);
        Assert.Equal(1, atFrameOne.BufferIndex);
    }

    // Pins the modulo wrap of eventmanager.cpp:253-254 (idiv by 0xC8 at
    // 0x0044B51E): the delayed bucket is relative to mCurrentBufferNum and wraps.
    // A rebuild that indexed absolutely, or clamped instead of wrapping, fails.
    [Fact]
    public void AddEvent_DelayedBucketIsRelativeToTheCurrentSlotAndWraps()
    {
        var scheduler = new RetailEventScheduler();
        for (int frame = 0; frame < 150; frame++)
        {
            scheduler.AdvanceTime();
            scheduler.Flush();
        }

        Assert.Equal(150, scheduler.CurrentBufferNum);

        // mTime is now 7.5; +9.9 is 197 slots out, so 150 + 197 wraps to 147.
        RetailEventAdmission wrapped =
            scheduler.AddEventTimeFromNow(9.9f, 11, Listener);
        Assert.Equal(RetailEventPlacement.DelayedBucket, wrapped.Placement);
        Assert.Equal(147, wrapped.BufferIndex);
    }

    // Pins the forwarder at 0x0044B2D0: time_from_now + mTime, then the ordinary
    // routing. At mTime = 0.05f a 0.2f delay is exactly 0.25f and lands 3 slots
    // out, not 4 - the -0.001f inclusive bias (eventmanager.cpp:209) is what
    // pulls 3.98 below 4. Removing that bias moves this to slot 5.
    [Fact]
    public void AddEventTimeFromNow_AddsCurrentTimeThenRoutesWithTheInclusiveBias()
    {
        var scheduler = new RetailEventScheduler();
        scheduler.AdvanceTime();

        RetailEventAdmission admission =
            scheduler.AddEventTimeFromNow(0.2f, 11, Listener);

        Assert.Equal(0x3E800000u, admission.DueTimeBits);
        Assert.Equal(RetailEventPlacement.DelayedBucket, admission.Placement);
        Assert.Equal(1 + 3, admission.BufferIndex);
    }

    // Pins the two silent refusals of 0x0044B370 and that neither consumes a
    // pool entry. A rebuild that threw, or that allocated before validating,
    // fails on the free-list count.
    [Fact]
    public void AddEvent_RefusesNullListenerAndInvalidManagerWithoutTakingAnEvent()
    {
        var scheduler = new RetailEventScheduler();
        int free = scheduler.FreeEventCount();

        Assert.Equal(
            RetailEventPlacement.RejectedNullListener,
            scheduler.AddEvent(1, 0, 0.05f).Placement);

        scheduler.Shutdown();
        Assert.Equal(
            RetailEventPlacement.RejectedInvalidManager,
            scheduler.AddEvent(1, Listener, 0.05f).Placement);

        Assert.Equal(free, scheduler.FreeEventCount());
        Assert.Equal(0, scheduler.TotalEvents);
    }

    // Pins the free list of eventmanager.cpp:58-64 and 129-135: Init chains the
    // pool ascending so the first handles are 0, 1, 2, and FreeEvent pushes onto
    // the HEAD, so the next allocation is the most recently freed. A FIFO
    // recycler produces 3 here instead of 1. Pool capacity is MAX_NUM_EVENTS from
    // eventmanager.h:20; that number is not itself read from the image.
    [Fact]
    public void FreeList_AllocatesAscendingAndRecyclesLastInFirstOut()
    {
        var scheduler = new RetailEventScheduler();
        Assert.Equal(RetailEventScheduler.MaxEvents, scheduler.FreeEventCount());
        Assert.Equal(0, scheduler.FreeListHead);

        int first = scheduler.AddEvent(1, Listener, 0.05f).Handle;
        int second = scheduler.AddEvent(2, Listener, 0.05f).Handle;
        int third = scheduler.AddEvent(3, Listener, 0.05f).Handle;
        Assert.Equal(0, first);
        Assert.Equal(1, second);
        Assert.Equal(2, third);

        scheduler.FreeEvent(second);
        Assert.Equal(second, scheduler.FreeListHead);
        Assert.Equal(second, scheduler.AddEvent(4, Listener, 0.05f).Handle);
    }

    // Pins the exhaustion arm: retail's GetNextFreeEvent returns NULL and
    // AddEvent returns without storing (0x0044B491 / 0x0044B54D), so the 20001st
    // simultaneous event is LOST, not queued or grown. Also pins that the drop
    // leaves TotalEvents at the pool size rather than incrementing.
    [Fact]
    public void AddEvent_DropsTheEventThatWouldExhaustThePool()
    {
        var scheduler = new RetailEventScheduler();
        for (int i = 0; i < RetailEventScheduler.MaxEvents; i++)
        {
            Assert.Equal(
                RetailEventPlacement.ImmediateBucket,
                scheduler.AddEvent(1, Listener, 0.05f).Placement);
        }

        Assert.Equal(0, scheduler.FreeEventCount());
        RetailEventAdmission overrun = scheduler.AddEvent(1, Listener, 0.05f);
        Assert.Equal(RetailEventPlacement.RejectedPoolExhausted, overrun.Placement);
        Assert.Equal(-1, overrun.Handle);
        Assert.Equal(RetailEventScheduler.MaxEvents, scheduler.TotalEvents);
    }

    // Pins the flush order of eventmanager.cpp:331-345: all three priority lanes
    // of the ready slot, in lane order, insertion order within a lane. Filing
    // END_OF_FRAME first and START_OF_FRAME last, then asserting the reverse
    // comes out, fails any implementation that ignores start_or_end or that
    // treats the lanes as one list. Does not pin what a listener does.
    [Fact]
    public void Flush_DrainsPriorityLanesInOrderAndInsertionOrderWithinALane()
    {
        var scheduler = new RetailEventScheduler();
        scheduler.AddEvent(30, Listener, 0.05f, RetailEventPriority.EndOfFrame);
        scheduler.AddEvent(20, Listener, 0.05f, RetailEventPriority.MiddleOfFrame);
        scheduler.AddEvent(11, Listener, 0.05f, RetailEventPriority.StartOfFrame);
        scheduler.AddEvent(12, Listener, 0.05f, RetailEventPriority.StartOfFrame);

        IReadOnlyList<RetailEventDispatch> dispatched = scheduler.Update();

        Assert.Equal(new[] { 11, 12, 20, 30 }, dispatched.Select(d => d.EventNum).ToArray());
        Assert.Equal(4u, scheduler.EventsProcessedInLastUpdate);
        Assert.Equal(4u, scheduler.TotalEventsProcessed);
        Assert.Equal(0, scheduler.TotalEvents);
        Assert.Equal(RetailEventScheduler.MaxEvents, scheduler.FreeEventCount());
    }

    // Pins the STRICT overflow gate at 0x0044B6D9 (test ah,1 / je - C0 only, so
    // "less than", never "equal"): an overflow event due exactly on the frame
    // boundary waits one more frame. 10.0f is due at frame 200 (mTime 10.0f
    // exactly) but only fires at frame 201. A <= gate fires it one frame early
    // and fails. Also pins eventmanager.h:38-41 - an overflow event runs after
    // every ring event of that frame whatever priority it carried.
    [Fact]
    public void Flush_OverflowGateIsStrictlyLessThanTheFrameTime()
    {
        var scheduler = new RetailEventScheduler();
        RetailEventAdmission overflow = scheduler.AddEvent(
            99, Listener, 10.0f, RetailEventPriority.StartOfFrame);
        Assert.Equal(RetailEventPlacement.Overflow, overflow.Placement);

        for (int frame = 0; frame < 200; frame++)
        {
            Assert.Empty(scheduler.Update());
        }

        Assert.Equal(0x41200000u, BitConverter.SingleToUInt32Bits(scheduler.Time));
        Assert.Equal(1, scheduler.TotalEvents);

        scheduler.AddEvent(1, Listener, 10.05f, RetailEventPriority.EndOfFrame);
        IReadOnlyList<RetailEventDispatch> fired = scheduler.Update();

        Assert.Equal(new[] { 1, 99 }, fired.Select(d => d.EventNum).ToArray());
        Assert.False(fired[0].FromOverflow);
        Assert.True(fired[1].FromOverflow);
        Assert.Equal(0, scheduler.TotalEvents);
    }

    // Pins the overflow insertion scan of eventmanager.cpp:222-226 (the <=
    // advance at 0x0044B459): the list stays sorted by due time, and an event
    // equal in time to a resident one is inserted AFTER it. Assert on indices,
    // so a stable sort by time alone would still have to place 13 at index 1 and
    // 12 at index 2 to pass.
    [Fact]
    public void AddEvent_KeepsTheOverflowListTimeOrderedAndStableOnTies()
    {
        var scheduler = new RetailEventScheduler();

        Assert.Equal(0, scheduler.AddEvent(11, Listener, 12.0f).OverflowIndex);
        Assert.Equal(0, scheduler.AddEvent(12, Listener, 10.0f).OverflowIndex);
        Assert.Equal(1, scheduler.AddEvent(13, Listener, 10.0f).OverflowIndex);
        Assert.Equal(3, scheduler.AddEvent(14, Listener, 14.0f).OverflowIndex);
        Assert.Equal(2, scheduler.AddEvent(15, Listener, 11.0f).OverflowIndex);
    }

    // Pins the int16 storage of the event number: CScheduledEvent::Set writes a
    // WORD (0x004DE1F0), and AddEvent(CScheduledEvent*) re-reads it with movsx
    // (0x0044B32E). 40000 comes back as -25536. A rebuild storing an int passes
    // 40000 through and fails. The source text says "const int event_num"
    // throughout and gives no hint of this.
    [Fact]
    public void AddEvent_StoresTheEventNumberAsSignedSixteenBits()
    {
        var scheduler = new RetailEventScheduler();
        RetailEventAdmission wide = scheduler.AddEvent(40_000, Listener, 0.05f);

        Assert.Equal(unchecked((short)40_000), scheduler.EventNumOf(wide.Handle));
        Assert.Equal(-25_536, scheduler.EventNumOf(wide.Handle));

        RetailEventDispatch fired = Assert.Single(scheduler.Update());
        Assert.Equal(-25_536, fired.EventNum);
    }

    // Pins the re-arm path that makes CPanCamera::Update (Camera.cpp:392) viable:
    // Flush clears mBeingReused before the callback, the callback re-files the
    // same event through re_use_event, and cleanup then skips the free while
    // still decrementing the live count (eventmanager.cpp:367-378). Run 200
    // frames: the handle never changes and the pool never drains. An
    // implementation that freed unconditionally loses the handle; one that
    // skipped the decrement leaks TotalEvents upward.
    [Fact]
    public void Flush_ReArmedEventKeepsItsHandleAndDoesNotDrainThePool()
    {
        var scheduler = new RetailEventScheduler();
        RetailEventAdmission seed = scheduler.AddEvent(
            2000, Listener, RetailEventScheduler.NextFrame, RetailEventPriority.EndOfFrame);
        int handle = seed.Handle;
        int freeAfterSeed = scheduler.FreeEventCount();

        var seen = new List<int>();
        void Repost(RetailEventScheduler owner, RetailEventDispatch dispatch)
        {
            seen.Add(dispatch.Handle);
            owner.AddEvent(
                dispatch.EventNum,
                dispatch.Listener,
                RetailEventScheduler.NextFrame,
                RetailEventPriority.EndOfFrame,
                data: 0,
                reuseHandle: dispatch.Handle);
        }

        for (int frame = 0; frame < 200; frame++)
        {
            Assert.Single(scheduler.Update(Repost));
        }

        Assert.Equal(200, seen.Count);
        Assert.All(seen, h => Assert.Equal(handle, h));
        Assert.Equal(1, scheduler.TotalEvents);
        Assert.Equal(freeAfterSeed, scheduler.FreeEventCount());
        Assert.True(scheduler.ReuseOf(handle));
    }

    // Pins eventmanager.cpp:152-162 / 0x0044B310: the owned event is re-filed at
    // its OWN time plus mTime - so a stored 0.0f becomes "now", not "at 0.0" -
    // always at START_OF_FRAME whatever it was, and the original handle is freed
    // rather than reused, so a different handle comes back.
    [Fact]
    public void AddOwnedEvent_RebasesOnCurrentTimeAtStartOfFrameAndFreesTheOriginal()
    {
        var scheduler = new RetailEventScheduler();
        scheduler.AdvanceTime();
        scheduler.Flush();

        int owned = scheduler.PrepareOwnedEvent(77, SecondListener, 0.2f);
        Assert.Equal(0x3E4CCCCDu, scheduler.DueTimeBitsOf(owned));
        Assert.Equal(0, scheduler.TotalEvents);

        RetailEventAdmission refiled = scheduler.AddOwnedEvent(owned);

        // mTime is 0.05f, the stored time is 0.2f, so the new due time is 0.25f
        // and the delayed bucket is 1 + floor(3.98) = 4.
        Assert.Equal(0x3E800000u, refiled.DueTimeBits);
        Assert.Equal(4, refiled.BufferIndex);
        Assert.NotEqual(owned, refiled.Handle);
        Assert.Equal(owned, scheduler.FreeListHead);
        Assert.Equal(1, scheduler.TotalEvents);

        // The lane is hard-coded to START_OF_FRAME (eventmanager.cpp:158) even
        // though nothing said so at the call site.
        RetailEventDispatch fired = default;
        for (int frame = 0; frame < 4; frame++)
        {
            IReadOnlyList<RetailEventDispatch> dispatched = scheduler.Update();
            if (dispatched.Count > 0)
            {
                fired = dispatched[0];
            }
        }

        Assert.Equal(refiled.Handle, fired.Handle);
        Assert.Equal(77, fired.EventNum);
        Assert.Equal(RetailEventPriority.StartOfFrame, fired.Priority);
    }

    // Pins that a null listener is still counted and still freed
    // (eventmanager.cpp:339-343 increments mTotalEventProcessedNum outside the
    // if). Modelled by freeing the event by hand, which is what retail's
    // CActiveReader does when the target dies: the slot survives in the ring but
    // dispatches nothing.
    [Fact]
    public void Flush_CountsAnEventWhoseListenerDiedButDoesNotDispatchIt()
    {
        var scheduler = new RetailEventScheduler();
        RetailEventAdmission doomed = scheduler.AddEvent(5, Listener, 0.05f);
        scheduler.AddEvent(6, SecondListener, 0.05f);

        // The reader has gone; retail's GetToCall() would now return NULL.
        scheduler.ClearListener(doomed.Handle);

        IReadOnlyList<RetailEventDispatch> fired = scheduler.Update();

        Assert.Equal(new[] { 6 }, fired.Select(d => d.EventNum).ToArray());
        Assert.Equal(2u, scheduler.EventsProcessedInLastUpdate);
        Assert.Equal(0, scheduler.TotalEvents);
        Assert.Equal(RetailEventScheduler.MaxEvents, scheduler.FreeEventCount());
    }
}
