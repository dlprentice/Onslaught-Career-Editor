/* address: 0x004be970 */
/* name: CExplosionInitThing__TestBitAtGridCoordPacked */
/* signature: uint __thiscall CExplosionInitThing__TestBitAtGridCoordPacked(void * this, int param_1, uint param_2, int param_3) */


uint __thiscall
CExplosionInitThing__TestBitAtGridCoordPacked(void *this,int param_1,uint param_2,int param_3)

{
  uint uVar1;

  uVar1 = param_1 & 0x80000007;
  if ((int)uVar1 < 0) {
    uVar1 = (uVar1 - 1 | 0xfffffff8) + 1;
  }
  return 1 << ((byte)uVar1 & 0x1f) & (uint)*(byte *)((param_1 >> 3) * 0x100 + param_2 + (int)this);
}
