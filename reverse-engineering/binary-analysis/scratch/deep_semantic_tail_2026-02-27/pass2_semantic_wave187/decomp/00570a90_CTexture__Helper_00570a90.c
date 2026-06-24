/* address: 0x00570a90 */
/* name: CTexture__Helper_00570a90 */
/* signature: int __thiscall CTexture__Helper_00570a90(void * this, int param_1, void * param_2, int param_3) */


int __thiscall CTexture__Helper_00570a90(void *this,int param_1,void *param_2,int param_3)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  bool bVar6;

  iVar1 = *(int *)(param_1 + 4);
  iVar5 = *(int *)param_1;
  uVar3 = CFastVB__FindEdgeRecord((int)param_2,iVar5,iVar1);
  iVar2 = *(int *)(uVar3 + 4);
  if (iVar2 != 0) {
    if (*(int *)((int)this + 0x20) < 0) {
      bVar6 = *(int *)(iVar2 + 0xc) == *(int *)((int)this + 0x1c);
    }
    else {
      bVar6 = *(int *)(iVar2 + 0x10) == *(int *)((int)this + 0x1c);
    }
    if (bVar6) goto LAB_00570bce;
  }
  iVar2 = *(int *)(uVar3 + 8);
  if (iVar2 != 0) {
    if (*(int *)((int)this + 0x20) < 0) {
      iVar4 = *(int *)((int)this + 0x1c);
      bVar6 = *(int *)(iVar2 + 0xc) == iVar4;
    }
    else {
      iVar4 = *(int *)(iVar2 + 0x10);
      bVar6 = iVar4 == *(int *)((int)this + 0x1c);
    }
    uVar3 = CONCAT31((int3)((uint)iVar4 >> 8),bVar6);
    if (bVar6 != false) goto LAB_00570bce;
  }
  iVar2 = *(int *)(param_1 + 8);
  uVar3 = CFastVB__FindEdgeRecord((int)param_2,iVar1,iVar2);
  iVar1 = *(int *)(uVar3 + 4);
  if (iVar1 != 0) {
    if (*(int *)((int)this + 0x20) < 0) {
      bVar6 = *(int *)(iVar1 + 0xc) == *(int *)((int)this + 0x1c);
    }
    else {
      bVar6 = *(int *)(iVar1 + 0x10) == *(int *)((int)this + 0x1c);
    }
    if (bVar6) goto LAB_00570bce;
  }
  iVar1 = *(int *)(uVar3 + 8);
  if (iVar1 != 0) {
    if (*(int *)((int)this + 0x20) < 0) {
      iVar4 = *(int *)(iVar1 + 0xc);
      bVar6 = iVar4 == *(int *)((int)this + 0x1c);
    }
    else {
      iVar4 = *(int *)((int)this + 0x1c);
      bVar6 = *(int *)(iVar1 + 0x10) == iVar4;
    }
    uVar3 = CONCAT31((int3)((uint)iVar4 >> 8),bVar6);
    if (bVar6 != false) goto LAB_00570bce;
  }
  uVar3 = CFastVB__FindEdgeRecord((int)param_2,iVar2,iVar5);
  iVar1 = *(int *)(uVar3 + 4);
  if (iVar1 != 0) {
    if (*(int *)((int)this + 0x20) < 0) {
      bVar6 = *(int *)(iVar1 + 0xc) == *(int *)((int)this + 0x1c);
    }
    else {
      bVar6 = *(int *)(iVar1 + 0x10) == *(int *)((int)this + 0x1c);
    }
    if (bVar6) goto LAB_00570bce;
  }
  iVar1 = *(int *)(uVar3 + 8);
  uVar3 = 0;
  if (iVar1 != 0) {
    if (*(int *)((int)this + 0x20) < 0) {
      iVar5 = *(int *)(iVar1 + 0xc);
      bVar6 = iVar5 == *(int *)((int)this + 0x1c);
    }
    else {
      iVar5 = *(int *)((int)this + 0x1c);
      bVar6 = *(int *)(iVar1 + 0x10) == iVar5;
    }
    uVar3 = CONCAT31((int3)((uint)iVar5 >> 8),bVar6);
    if (bVar6 != false) {
LAB_00570bce:
      return CONCAT31((int3)(uVar3 >> 8),1);
    }
  }
  return uVar3 & 0xffffff00;
}
