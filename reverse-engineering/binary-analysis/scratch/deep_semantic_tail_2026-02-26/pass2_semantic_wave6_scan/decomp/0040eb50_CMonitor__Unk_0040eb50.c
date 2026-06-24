/* address: 0x0040eb50 */
/* name: CMonitor__Unk_0040eb50 */
/* signature: void __fastcall CMonitor__Unk_0040eb50(int param_1) */


void __fastcall CMonitor__Unk_0040eb50(int param_1)

{
  undefined4 *puVar1;
  int iVar2;
  void *this;
  int *piVar3;
  int unaff_ESI;
  int unaff_EDI;

  if (*(int *)(param_1 + 0x1e4) != 0) {
    iVar2 = CExplosionInitThing__Helper_004725d0(0x8a9a98);
    if (iVar2 != 0) {
      puVar1 = *(undefined4 **)(param_1 + 0x1d4);
      if (puVar1 == (undefined4 *)0x0) {
        this = (void *)0x0;
      }
      else {
        this = (void *)*puVar1;
      }
      while (this != (void *)0x0) {
        CUnit__Helper_004cb0b0(this,0,unaff_ESI);
        puVar1 = (undefined4 *)puVar1[1];
        if (puVar1 == (undefined4 *)0x0) {
          this = (void *)0x0;
        }
        else {
          this = (void *)*puVar1;
        }
      }
    }
    piVar3 = CMonitor__Helper_004e1880
                       (&DAT_00896988,*(int *)(param_1 + 0x59c) + 0x40,(void *)param_1,unaff_ESI);
    if ((piVar3 != (int *)0x0) && (*(int *)(param_1 + 0x260) == 2)) {
      CMonitor__Helper_004e1260(&DAT_00896988,piVar3[3],0,0.02,(float)param_1,unaff_EDI);
    }
    *(undefined4 *)(param_1 + 0x1e4) = 0;
  }
  return;
}
