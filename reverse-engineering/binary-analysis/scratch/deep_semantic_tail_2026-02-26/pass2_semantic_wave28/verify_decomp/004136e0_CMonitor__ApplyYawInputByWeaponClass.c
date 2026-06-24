/* address: 0x004136e0 */
/* name: CMonitor__ApplyYawInputByWeaponClass */
/* signature: void __thiscall CMonitor__ApplyYawInputByWeaponClass(void * this, int param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CMonitor__ApplyYawInputByWeaponClass(void *this,int param_1,float param_2)

{
  int iVar1;
  float fVar2;
  double dVar3;
  float local_8;

  iVar1 = *(int *)((int)this + 0x20);
  if (((&DAT_00889304)[(*(int *)(*(int *)(iVar1 + 0x574) + 0x2c) + -1) * 3] == 0xc) ||
     (local_8 = 1.0, (&DAT_00889304)[(*(int *)(*(int *)(iVar1 + 0x574) + 0x2c) + -1) * 3] == 0xb)) {
    local_8 = 1.7;
  }
  fVar2 = *(float *)(iVar1 + 0x280);
  dVar3 = CGeneralVolume__Helper_00409e60(*(float *)(iVar1 + 0x2c8));
  *(float *)(*(int *)((int)this + 0x20) + 0x280) =
       fVar2 - local_8 * (float)param_1 * _DAT_005d8c90 * (float)dVar3;
  return;
}
