/* address: 0x0058546f */
/* name: CMeshCollisionVolume__Unk_0058546f */
/* signature: void __thiscall CMeshCollisionVolume__Unk_0058546f(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Removing unreachable block (ram,0x005854e2) */
/* WARNING: Removing unreachable block (ram,0x005854c0) */
/* WARNING: Removing unreachable block (ram,0x00585510) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CMeshCollisionVolume__Unk_0058546f(void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  uint *puVar1;
  float fVar2;
  ushort uVar3;
  uint *puVar4;
  uint unaff_EDI;

  puVar4 = (uint *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  puVar1 = puVar4 + *(int *)((int)this + 0x1060) * 2;
  fVar2 = _DAT_005e9f34;
  for (; puVar4 < puVar1; puVar4 = puVar4 + 2) {
    *(float *)param_3 = (float)(*puVar4 & 0xffff) * fVar2;
    *(float *)(param_3 + 4) = (float)(*puVar4 >> 0x10) * fVar2;
    uVar3 = __aullshr();
    fVar2 = _DAT_005e9f34;
    *(float *)(param_3 + 8) = (float)uVar3 * _DAT_005e9f34;
    *(float *)(param_3 + 0xc) = (float)*(ushort *)((int)puVar4 + 6) * fVar2;
    param_3 = (int)(param_3 + 0x10);
  }
  if (*(int *)((int)this + 0x18) != 0) {
    CFastVB__Helper_00581e1c(this,(int)(param_3 + *(int *)((int)this + 0x1060) * -4 * 4),unaff_EDI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    CTexture__Helper_0058210e(this,(int)(param_3 + *(int *)((int)this + 0x1060) * -4 * 4),unaff_EDI)
    ;
  }
  return;
}
