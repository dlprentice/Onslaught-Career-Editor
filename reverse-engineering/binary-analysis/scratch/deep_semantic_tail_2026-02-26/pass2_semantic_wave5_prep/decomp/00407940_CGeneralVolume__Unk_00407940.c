/* address: 0x00407940 */
/* name: CGeneralVolume__Unk_00407940 */
/* signature: void __thiscall CGeneralVolume__Unk_00407940(void * this, int param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CGeneralVolume__Unk_00407940(void *this,int param_1,float param_2)

{
  float fVar1;
  uint uVar2;
  float unaff_ESI;

  if ((float)_DAT_005d8bc8 <= (float)param_1) {
    if (_DAT_005d8bc4 < (float)param_1) {
      param_1 = 0x3f400000;
    }
    fVar1 = _DAT_005d8bc0 / (float)param_1;
    uVar2 = Random__NextLCGAbs(DAT_008a9d9c);
    uVar2 = uVar2 & 0x8000001f;
    if ((int)uVar2 < 0) {
      uVar2 = (uVar2 - 1 | 0xffffffe0) + 1;
    }
    *(float *)((int)this + 0x4b8) = (float)(int)uVar2 / fVar1 - (float)param_1;
    uVar2 = Random__NextLCGAbs(DAT_008a9d9c);
    uVar2 = uVar2 & 0x8000001f;
    if ((int)uVar2 < 0) {
      uVar2 = (uVar2 - 1 | 0xffffffe0) + 1;
    }
    *(float *)((int)this + 0x4bc) = (float)(int)uVar2 / fVar1 - (float)param_1;
    uVar2 = Random__NextLCGAbs(DAT_008a9d9c);
    uVar2 = uVar2 & 0x8000001f;
    if ((int)uVar2 < 0) {
      uVar2 = (uVar2 - 1 | 0xffffffe0) + 1;
    }
    *(undefined4 *)((int)this + 0x4c4) = 0;
    *(float *)((int)this + 0x4c0) = (float)(int)uVar2 / fVar1 - (float)param_1;
    if (*(void **)((int)this + 0x528) != (void *)0x0) {
      CGeneralVolume__Helper_004247a0(*(void **)((int)this + 0x528),param_1,unaff_ESI);
    }
    CFrontEndPage__Process_NoOp
              ((void *)(*(int *)(*(int *)((int)this + 0x574) + 0x2c) + -1),(int)unaff_ESI);
  }
  return;
}
