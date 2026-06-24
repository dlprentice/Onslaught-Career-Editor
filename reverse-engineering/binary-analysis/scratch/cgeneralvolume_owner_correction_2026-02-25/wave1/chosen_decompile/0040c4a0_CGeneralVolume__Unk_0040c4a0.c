/* address: 0x0040c4a0 */
/* name: CGeneralVolume__Unk_0040c4a0 */
/* signature: double __fastcall CGeneralVolume__Unk_0040c4a0(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CGeneralVolume__Unk_0040c4a0(int param_1)

{
  int iVar1;
  double dVar2;
  undefined1 local_10 [4];
  float fStack_c;

  iVar1 = stricmp(*(char **)(*(int *)(param_1 + 0x4b0) + 0xa8),s_Racer_006234f4);
  if (iVar1 == 0) {
    (*(code *)**(undefined4 **)(param_1 + 8))(local_10);
    dVar2 = CHeightField__Unk_0047eb80(0x6fadc8,&stack0xffffffec);
    if ((double)DAT_006fbdfc < dVar2) {
      dVar2 = (double)DAT_006fbdfc;
    }
    dVar2 = ABS(dVar2 - (double)fStack_c) * (double)_DAT_005d8c68;
    if ((double)_DAT_005d8568 < dVar2) {
      return (double)_DAT_005d8568;
    }
  }
  else {
    if (*(int *)(param_1 + 0x260) != 3) {
      dVar2 = CGeneralVolume__Unk_00414520(*(void **)(param_1 + 0x578));
      return dVar2;
    }
    dVar2 = CGeneralVolume__Unk_00412370(*(void **)(param_1 + 0x57c));
  }
  return dVar2;
}
