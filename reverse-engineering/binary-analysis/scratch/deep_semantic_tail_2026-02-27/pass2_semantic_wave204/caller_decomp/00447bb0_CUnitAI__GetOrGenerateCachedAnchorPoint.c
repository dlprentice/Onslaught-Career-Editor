/* address: 0x00447bb0 */
/* name: CUnitAI__GetOrGenerateCachedAnchorPoint */
/* signature: void __thiscall CUnitAI__GetOrGenerateCachedAnchorPoint(void * this, int param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CUnitAI__GetOrGenerateCachedAnchorPoint(void *this,int param_1,void *param_2)

{
  float fVar1;
  int iVar2;
  uint uVar3;
  float unaff_EDI;
  uint local_64;
  undefined4 local_54;
  undefined1 local_30 [4];
  float local_2c;
  float local_1c;
  float local_c;

  if (*(int *)((int)this + 0x294) == 0) {
    if (*(int *)((int)this + 0x290) == 0) {
      *(float *)((int)this + 0x280) = _DAT_005d856c + *(float *)((int)this + 0x1c);
      *(undefined4 *)((int)this + 0x290) = 1;
      *(float *)((int)this + 0x284) = *(float *)((int)this + 0x20) + 0.0;
      *(float *)((int)this + 0x288) = *(float *)((int)this + 0x24) + 0.0;
      *(undefined4 *)((int)this + 0x28c) = local_54;
    }
    local_64 = 0;
    iVar2 = CUnitAI__Helper_00447d50(this);
    if (iVar2 == 0) {
      do {
        if (7999 < (int)local_64) goto LAB_00447d0c;
        uVar3 = local_64 & 0x8000001f;
        fVar1 = (float)(int)local_64 * _DAT_005db250;
        if ((int)uVar3 < 0) {
          uVar3 = (uVar3 - 1 | 0xffffffe0) + 1;
        }
        CSquadNormal__Helper_004062d0
                  (local_30,(void *)((float)(int)uVar3 * _DAT_005d943c),0.0,0.0,unaff_EDI);
        local_64 = local_64 + 1;
        *(float *)((int)this + 0x280) = local_2c * fVar1 + *(float *)((int)this + 0x1c);
        *(float *)((int)this + 0x284) = local_1c * fVar1 + *(float *)((int)this + 0x20);
        *(float *)((int)this + 0x288) = local_c * fVar1 + *(float *)((int)this + 0x24);
        *(undefined4 *)((int)this + 0x28c) = local_54;
        iVar2 = CUnitAI__Helper_00447d50(this);
      } while (iVar2 == 0);
      if (7999 < (int)local_64) {
LAB_00447d0c:
        *(undefined4 *)((int)this + 0x290) = 0;
      }
    }
  }
  *(undefined4 *)param_1 = *(undefined4 *)((int)this + 0x280);
  *(undefined4 *)(param_1 + 4) = *(undefined4 *)((int)this + 0x284);
  *(undefined4 *)(param_1 + 8) = *(undefined4 *)((int)this + 0x288);
  *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)((int)this + 0x28c);
  return;
}
