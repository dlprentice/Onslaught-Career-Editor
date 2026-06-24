/* address: 0x00414cb0 */
/* name: CExplosionInitThing__Unk_00414cb0 */
/* signature: void __fastcall CExplosionInitThing__Unk_00414cb0(int param_1) */


void __fastcall CExplosionInitThing__Unk_00414cb0(int param_1)

{
  int iVar1;
  int iVar2;
  uint unaff_EDI;

  *(undefined4 *)(param_1 + 0x60) = 0;
  DAT_00855148 = DAT_00855140;
  if (DAT_00855140 == (int *)0x0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *DAT_00855140;
  }
  while (iVar2 != 0) {
    CExplosionInitThing__Helper_0053b5f0
              ((void *)param_1,*(int *)(iVar2 + 0x1c),*(float *)(iVar2 + 0x20),2.3509528e-38,
               unaff_EDI);
    DAT_00855148 = (int *)DAT_00855148[1];
    if (DAT_00855148 == (int *)0x0) {
      iVar2 = 0;
    }
    else {
      iVar2 = *DAT_00855148;
    }
  }
  DAT_008550a8 = DAT_008550a0;
  if (DAT_008550a0 == (int *)0x0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *DAT_008550a0;
  }
  while (iVar2 != 0) {
    iVar1 = CExplosionInitThing__Helper_004e6610(iVar2);
    if (iVar1 == 1) {
      CExplosionInitThing__Helper_0053b5f0
                ((void *)param_1,*(int *)(iVar2 + 0x1c),*(float *)(iVar2 + 0x20),2.3420933e-38,
                 unaff_EDI);
    }
    DAT_008550a8 = (int *)DAT_008550a8[1];
    if (DAT_008550a8 == (int *)0x0) {
      iVar2 = 0;
    }
    else {
      iVar2 = *DAT_008550a8;
    }
  }
  return;
}
