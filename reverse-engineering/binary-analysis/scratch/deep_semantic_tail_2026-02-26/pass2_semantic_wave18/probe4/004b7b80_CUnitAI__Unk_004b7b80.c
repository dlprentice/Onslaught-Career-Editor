/* address: 0x004b7b80 */
/* name: CUnitAI__Unk_004b7b80 */
/* signature: void __fastcall CUnitAI__Unk_004b7b80(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnitAI__Unk_004b7b80(void *param_1)

{
  undefined4 *puVar1;
  int iVar2;
  void *unaff_EDI;
  int *value;
  void *pvStack_4;

  iVar2 = *(int *)((int)param_1 + 0x18);
  pvStack_4 = param_1;
  while( true ) {
    if (iVar2 == 0) {
      return;
    }
    if (*(int *)((int)param_1 + 8) != 0) {
      return;
    }
    if (*(int *)((int)param_1 + 0x30) == 0) {
      return;
    }
    if (*(int *)((int)param_1 + 0x2c0) == 0) break;
    if (3 < DAT_008a9ac0) {
      return;
    }
    puVar1 = *(undefined4 **)((int)param_1 + 0xc);
    *(undefined4 **)((int)param_1 + 0x14) = puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      value = (int *)0x0;
    }
    else {
      value = (int *)*puVar1;
    }
    if ((value[0xe] == 0) || ((value[0xc] != 0 && ((*(byte *)(value[0xc] + 0x2c) & 4) == 0)))) {
      *(int **)((int)param_1 + 8) = value;
      *(float *)((int)param_1 + 0x1c) = DAT_00672fd0;
      *(undefined4 *)((int)param_1 + 0x30) = 0;
      *(undefined4 *)((int)param_1 + 0x20) = 0x3f800000;
      *(undefined1 *)((int)param_1 + 0x1c0) = 0;
      *(undefined4 *)((int)param_1 + 0x24) = 0;
      if (value[0xc] != 0) {
        CFrontEndPage__Process_NoOp(value + 0xc,(int)unaff_EDI);
      }
      iVar2 = CDropship__SelectPortraitIndex
                        (param_1,*(int *)(*(int *)((int)param_1 + 8) + 0x18),unaff_EDI);
      *(int *)((int)param_1 + 0x1a8) = iVar2;
      *(undefined4 *)((int)param_1 + 0x1ac) = 0;
      *(undefined4 *)((int)param_1 + 0x1b0) = *(undefined4 *)((int)param_1 + iVar2 * 0x18 + 0x34);
      *(float *)((int)param_1 + 0x1b4) = DAT_00672fd0;
      *(float *)(*(int *)((int)param_1 + 8) + 0x24) = _DAT_008a9bb0 + DAT_00672fd0;
      pvStack_4 = (void *)0x3e4ccccd;
      CEventManager__AddEvent_TimeFromNow
                (&EVENT_MANAGER,(float *)&pvStack_4,0xbbc,param_1,0,(void *)0x0,(void *)0x0);
      return;
    }
    CSPtrSet__Remove((void *)((int)param_1 + 0xc),value);
    if (value != (int *)0x0) {
      (**(code **)(*value + 4))(1);
    }
    iVar2 = *(int *)((int)param_1 + 0x18);
  }
  return;
}
