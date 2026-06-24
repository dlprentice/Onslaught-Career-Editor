/* address: 0x0059a54d */
/* name: CFastVB__ScoreNodeTreeMatch */
/* signature: int __thiscall CFastVB__ScoreNodeTreeMatch(void * this, void * param_1, int param_2, void * param_3, int param_4, uint param_5) */


int __thiscall
CFastVB__ScoreNodeTreeMatch
          (void *this,void *param_1,int param_2,void *param_3,int param_4,uint param_5)

{
  int *piVar1;
  byte bVar2;
  void *pvVar3;
  int iVar4;
  byte *pbVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  byte *pbVar9;
  void *unaff_EDI;
  bool bVar10;
  undefined1 local_24 [4];
  uint local_20;
  undefined1 local_18 [4];
  uint local_14;
  void *local_c;
  int local_8;

  local_8 = 0;
  local_c = this;
  if ((param_2 == 0) || (*(int *)((int)param_1 + 0x1c) == 0)) {
    if ((param_2 == 0) != (*(int *)((int)param_1 + 0x1c) == 0)) {
      local_8 = 2;
    }
  }
  else {
    iVar4 = CFastVB__Helper_00579b39(*(void **)(*(int *)((int)param_1 + 0x1c) + 0x18),0,local_18);
    if ((iVar4 < 0) ||
       (iVar4 = CFastVB__Helper_00579b39(*(void **)(param_2 + 0x18),0,local_24), iVar4 < 0)) {
      pbVar9 = *(byte **)(*(int *)((int)param_1 + 0x1c) + 0x18);
      pbVar5 = *(byte **)(param_2 + 0x18);
      do {
        bVar2 = *pbVar5;
        bVar10 = bVar2 < *pbVar9;
        if (bVar2 != *pbVar9) {
LAB_0059a600:
          iVar4 = (1 - (uint)bVar10) - (uint)(bVar10 != 0);
          goto LAB_0059a605;
        }
        if (bVar2 == 0) break;
        bVar2 = pbVar5[1];
        bVar10 = bVar2 < pbVar9[1];
        if (bVar2 != pbVar9[1]) goto LAB_0059a600;
        pbVar5 = pbVar5 + 2;
        pbVar9 = pbVar9 + 2;
      } while (bVar2 != 0);
      iVar4 = 0;
LAB_0059a605:
      if (iVar4 != 0) {
        return -1;
      }
    }
    else if (local_14 != local_20) {
      if (((local_20 ^ local_14) & 0xffff0000) != 0) {
        return -1;
      }
      if (((local_14 & 0xffff) != 0) && ((local_20 & 0xffff) != 0)) {
        return -1;
      }
      local_8 = 2 - (uint)((local_20 & 0xffff) != 0);
    }
  }
  iVar4 = *(int *)((int)param_1 + 0x24);
  param_1 = param_3;
  if (iVar4 != 0) {
    do {
      piVar1 = (int *)(iVar4 + 8);
      iVar4 = *(int *)(iVar4 + 0xc);
      bVar10 = false;
      if ((iVar4 != 0) && (*(int *)(*(int *)(iVar4 + 8) + 4) == 0xb)) {
        iVar4 = *(int *)(iVar4 + 0xc);
        bVar10 = true;
      }
      if (((param_4 & 0x10U) == 0) || ((*(byte *)(*(int *)(*piVar1 + 0x18) + 0x1c) & 0x40) != 0)) {
        if (param_1 == (void *)0x0) {
          if (!bVar10) {
            return -1;
          }
        }
        else {
          iVar8 = *(int *)(*piVar1 + 0x18);
          pvVar3 = *(void **)(iVar8 + 0x20);
          if (*(int *)((int)param_1 + 8) == 0) {
            param_2 = 0;
          }
          else {
            param_2 = *(int *)(*(int *)((int)param_1 + 8) + 0x10);
          }
          if ((*(byte *)(iVar8 + 0x1c) & 0x10) != 0) {
            iVar6 = CFastVB__AreNodeTreesCompatible(pvVar3,(void *)param_2,0);
            if (iVar6 == 0) {
              return -1;
            }
            iVar6 = CFastVB__Helper_0059a10a(local_c,pvVar3,(void *)param_2,unaff_EDI);
            local_8 = local_8 + iVar6;
          }
          if ((*(byte *)(iVar8 + 0x1c) & 0x20) != 0) {
            uVar7 = CFastVB__NodeTreeHasBitFlag0x200(local_c,param_2,(int)unaff_EDI);
            if (uVar7 != 0) {
              return -1;
            }
            iVar8 = CFastVB__AreNodeTreesCompatible((void *)param_2,pvVar3,0);
            if (iVar8 == 0) {
              return -1;
            }
            iVar8 = CFastVB__Helper_0059a10a(local_c,(void *)param_2,pvVar3,unaff_EDI);
            local_8 = local_8 + iVar8;
          }
          param_1 = *(void **)((int)param_1 + 0xc);
        }
      }
    } while (iVar4 != 0);
  }
  if (param_1 != (void *)0x0) {
    return -1;
  }
  return local_8;
}
