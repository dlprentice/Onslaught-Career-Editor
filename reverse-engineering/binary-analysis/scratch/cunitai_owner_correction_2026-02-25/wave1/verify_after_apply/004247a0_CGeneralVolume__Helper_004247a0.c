/* address: 0x004247a0 */
/* name: CGeneralVolume__Helper_004247a0 */
/* signature: void __thiscall CGeneralVolume__Helper_004247a0(void * this, int param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CGeneralVolume__Helper_004247a0(void *this,int param_1,float param_2)

{
  float fVar1;
  float fVar2;
  uint uVar3;

  fVar1 = _DAT_005d95b8 / (float)param_1;
  fVar2 = (float)param_1 * _DAT_005d85ec;
  uVar3 = _rand();
  uVar3 = uVar3 & 0x8000007f;
  if ((int)uVar3 < 0) {
    uVar3 = (uVar3 - 1 | 0xffffff80) + 1;
  }
  *(float *)((int)this + 0x90) = (float)(int)uVar3 / fVar1 - fVar2;
  uVar3 = _rand();
  uVar3 = uVar3 & 0x8000007f;
  if ((int)uVar3 < 0) {
    uVar3 = (uVar3 - 1 | 0xffffff80) + 1;
  }
  *(float *)((int)this + 0x94) = (float)(int)uVar3 / fVar1 - fVar2;
  uVar3 = _rand();
  uVar3 = uVar3 & 0x8000007f;
  if ((int)uVar3 < 0) {
    uVar3 = (uVar3 - 1 | 0xffffff80) + 1;
  }
  *(float *)((int)this + 0x98) = (float)(int)uVar3 / fVar1 - fVar2;
  uVar3 = _rand();
  uVar3 = uVar3 & 0x8000001f;
  if ((int)uVar3 < 0) {
    uVar3 = (uVar3 - 1 | 0xffffffe0) + 1;
  }
  *(undefined4 *)((int)this + 0xa0) = 0;
  *(float *)((int)this + 0x9c) = (float)(int)uVar3 / fVar1 - fVar2;
  if (*(float *)((int)this + 0x90) <= _DAT_005d8574) {
    if (*(float *)((int)this + 0x90) < _DAT_005d95b4) {
      *(undefined4 *)((int)this + 0x90) = 0xbc23d70a;
    }
  }
  else {
    *(undefined4 *)((int)this + 0x90) = 0x3c23d70a;
  }
  if (*(float *)((int)this + 0x94) <= _DAT_005d8574) {
    if (*(float *)((int)this + 0x94) < _DAT_005d95b4) {
      *(undefined4 *)((int)this + 0x94) = 0xbc23d70a;
    }
  }
  else {
    *(undefined4 *)((int)this + 0x94) = 0x3c23d70a;
  }
  if (_DAT_005d8574 < *(float *)((int)this + 0x98)) {
    *(undefined4 *)((int)this + 0x98) = 0x3c23d70a;
    return;
  }
  if (*(float *)((int)this + 0x98) < _DAT_005d95b4) {
    *(undefined4 *)((int)this + 0x98) = 0xbc23d70a;
  }
  return;
}
