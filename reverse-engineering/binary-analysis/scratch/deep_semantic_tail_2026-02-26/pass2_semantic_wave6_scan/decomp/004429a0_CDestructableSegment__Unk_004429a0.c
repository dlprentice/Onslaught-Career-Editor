/* address: 0x004429a0 */
/* name: CDestructableSegment__Unk_004429a0 */
/* signature: void __fastcall CDestructableSegment__Unk_004429a0(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CDestructableSegment__Unk_004429a0(void *param_1)

{
  undefined4 *puVar1;
  int iVar2;
  uint uVar3;
  int *to_call;
  void *pvStack_4;

  puVar1 = *(undefined4 **)((int)param_1 + 0x24);
  pvStack_4 = param_1;
  if (puVar1 == (undefined4 *)0x0) {
    to_call = (int *)0x0;
  }
  else {
    to_call = (int *)*puVar1;
  }
  while (to_call != (int *)0x0) {
    iVar2 = (**(code **)(*(int *)param_1 + 0x14))();
    if (iVar2 == 0) {
      (**(code **)(*to_call + 0x20))();
    }
    else {
      iVar2 = (**(code **)(*(int *)param_1 + 0x14))();
      if (iVar2 == 1) {
        uVar3 = _rand();
        pvStack_4 = (void *)((float)(int)((uVar3 & 0xff) - 0x80) * _DAT_005db060 + _DAT_005d85ec +
                            DAT_00672fd0);
      }
      else {
        uVar3 = _rand();
        pvStack_4 = (void *)((float)(int)((uVar3 & 0xff) - 0x80) * _DAT_005db05c + _DAT_005d85c0 +
                            DAT_00672fd0);
      }
      CEventManager__AddEvent_AtTime
                (&EVENT_MANAGER,3000,to_call,(float *)&pvStack_4,0,(void *)0x0,(void *)0x0);
    }
    puVar1 = (undefined4 *)puVar1[1];
    if (puVar1 == (undefined4 *)0x0) {
      to_call = (int *)0x0;
    }
    else {
      to_call = (int *)*puVar1;
    }
  }
  return;
}
