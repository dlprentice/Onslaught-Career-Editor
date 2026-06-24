/* address: 0x00479d10 */
/* name: CUnitAI__Unk_00479d10 */
/* signature: void __fastcall CUnitAI__Unk_00479d10(int param_1) */


void __fastcall CUnitAI__Unk_00479d10(int param_1)

{
  undefined4 uVar1;
  double dVar2;

  uVar1 = DAT_00672fd0;
  if (*(int *)(param_1 + 0x274) != 1) {
    if (*(int *)(param_1 + 0x244) == 2) {
      *(undefined4 *)(param_1 + 0x84) = 0x3df5c28f;
      *(undefined4 *)(param_1 + 0xcc) = uVar1;
    }
    CExplosionInitThing__ctor_like_0049fc10((void *)param_1);
    return;
  }
  *(undefined4 *)(param_1 + 0xcc) = DAT_00672fd0;
  dVar2 = CStaticShadows__Helper_0047eb80(0x6fadc8,(void *)(param_1 + 0x1c));
  if ((double)*(float *)(param_1 + 0x24) <= dVar2) {
    *(undefined4 *)(param_1 + 0x274) = 0;
    *(undefined4 *)(param_1 + 0x84) = 0;
    CExplosionInitThing__ctor_like_0049fc10((void *)param_1);
    return;
  }
  *(undefined4 *)(param_1 + 0x84) = 0xbda3d70a;
  CExplosionInitThing__ctor_like_0049fc10((void *)param_1);
  return;
}
