/* address: 0x004e8100 */
/* name: CSquadNormal__ScheduleTargetReaderRefresh */
/* signature: void __fastcall CSquadNormal__ScheduleTargetReaderRefresh(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CSquadNormal__ScheduleTargetReaderRefresh(void *param_1)

{
  int *to_read;
  uint uVar1;
  void *local_4;

  local_4 = param_1;
  if ((*(int *)((int)param_1 + 0x114) != 0) && (*(int *)((int)param_1 + 0x120) != 1)) {
    if (*(int *)((int)param_1 + 0xc4) == 0) {
      *(undefined4 *)((int)param_1 + 0xcc) = 0;
    }
    if (*(int *)((int)param_1 + 0xcc) == 0) {
      to_read = (int *)0x0;
      if ((*(int *)((int)param_1 + 0x7c) == 1) || (*(int *)((int)param_1 + 0x7c) == 0)) {
        to_read = CSquadNormal__Helper_00477cb0(param_1);
      }
      CGenericActiveReader__SetReader((void *)((int)param_1 + 0xc4),to_read);
      *(undefined4 *)((int)param_1 + 0xcc) = 0;
    }
  }
  uVar1 = Random__NextLCGAbs(DAT_008a9d9c);
  uVar1 = uVar1 & 0x8000ffff;
  if ((int)uVar1 < 0) {
    uVar1 = (uVar1 - 1 | 0xffff0000) + 1;
  }
  local_4 = (void *)((float)(int)uVar1 * _DAT_005d8de4 + _DAT_005d8ba0 + DAT_00672fd0);
  CEventManager__AddEvent_AtTime
            (&EVENT_MANAGER,4000,param_1,(float *)&local_4,0,(void *)0x0,(void *)0x0);
  return;
}
