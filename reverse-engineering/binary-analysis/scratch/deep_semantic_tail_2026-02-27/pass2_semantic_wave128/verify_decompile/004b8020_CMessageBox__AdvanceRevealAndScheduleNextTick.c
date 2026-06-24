/* address: 0x004b8020 */
/* name: CMessageBox__AdvanceRevealAndScheduleNextTick */
/* signature: void __fastcall CMessageBox__AdvanceRevealAndScheduleNextTick(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CMessageBox__AdvanceRevealAndScheduleNextTick(void *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  void *local_4;

  iVar1 = *(int *)((int)param_1 + 8);
  local_4 = param_1;
  if ((*(int *)(iVar1 + 0x38) != 0) &&
     ((*(int *)(iVar1 + 0x30) == 0 || ((*(byte *)(*(int *)(iVar1 + 0x30) + 0x2c) & 4) != 0)))) {
    *(undefined4 *)((int)param_1 + 0x20) = 0x3f800000;
    iVar2 = WcsLen(*(short **)(iVar1 + 0xc));
    if (*(int *)(iVar1 + 0x1c) < iVar2) {
      CMessageBox__StopVoicePlaybackIfNotInCutscene((int)param_1);
      *(int *)(*(int *)((int)param_1 + 8) + 0x34) = *(int *)(*(int *)((int)param_1 + 8) + 0x34) + 1;
      if (*(int *)(*(int *)((int)param_1 + 8) + 0x34) < 5) {
        local_4 = (void *)0x3d1ba5e3;
        CEventManager__AddEvent_TimeFromNow
                  (&EVENT_MANAGER,(float *)&local_4,3000,param_1,0,(void *)0x0,(void *)0x0);
        return;
      }
      *(undefined4 *)((int)param_1 + 0x24) = 1;
      local_4 = (void *)0x402ccccd;
      CEventManager__AddEvent_TimeFromNow
                (&EVENT_MANAGER,(float *)&local_4,0xbba,param_1,0,(void *)0x0,(void *)0x0);
      return;
    }
    *(undefined4 *)((int)param_1 + 0x24) = 1;
  }
  iVar1 = *(int *)((int)param_1 + 8);
  iVar2 = *(int *)(iVar1 + 0x1c);
  iVar3 = WcsLen(*(short **)(iVar1 + 0xc));
  if (iVar2 < iVar3) {
    *(int *)(iVar1 + 0x1c) = iVar2 + 1;
  }
  iVar2 = *(int *)(iVar1 + 0x1c);
  iVar3 = WcsLen(*(short **)(iVar1 + 0xc));
  if (iVar2 < iVar3) {
    *(int *)(iVar1 + 0x1c) = iVar2 + 1;
  }
  if (DAT_00672fd0 <
      *(float *)(*(int *)((int)param_1 + 8) + 0x14) + *(float *)((int)param_1 + 0x1c) +
      _DAT_005d8604) {
    local_4 = (void *)0x3d1ba5e3;
    CEventManager__AddEvent_TimeFromNow
              (&EVENT_MANAGER,(float *)&local_4,3000,param_1,0,(void *)0x0,(void *)0x0);
    return;
  }
  if ((*(int *)(*(int *)((int)param_1 + 8) + 8) != 1) &&
     (DAT_00672fd0 - *(float *)((int)param_1 + 0x1c) <= _DAT_005db4e8)) {
    local_4 = (void *)0x3d1ba5e3;
    CEventManager__AddEvent_TimeFromNow
              (&EVENT_MANAGER,(float *)&local_4,3000,param_1,0,(void *)0x0,(void *)0x0);
    return;
  }
  *(undefined4 *)((int)param_1 + 0x20) = 0x3f800000;
  *(undefined4 *)((int)param_1 + 0x24) = 1;
  local_4 = (void *)0x3e99999a;
  CEventManager__AddEvent_TimeFromNow
            (&EVENT_MANAGER,(float *)&local_4,0xbba,param_1,0,(void *)0x0,(void *)0x0);
  return;
}
