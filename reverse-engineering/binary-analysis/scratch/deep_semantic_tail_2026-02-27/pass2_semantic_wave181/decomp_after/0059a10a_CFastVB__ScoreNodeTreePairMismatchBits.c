/* address: 0x0059a10a */
/* name: CFastVB__ScoreNodeTreePairMismatchBits */
/* signature: int __thiscall CFastVB__ScoreNodeTreePairMismatchBits(void * this, void * param_1, void * param_2, void * param_3) */


int __thiscall
CFastVB__ScoreNodeTreePairMismatchBits(void *this,void *param_1,void *param_2,void *param_3)

{
  bool bVar1;
  undefined3 extraout_var;
  int iVar2;
  int unaff_EBX;
  int unaff_EDI;
  uint uVar3;
  undefined1 local_60 [20];
  int local_4c;
  undefined1 local_3c [20];
  int local_28;
  int local_18;
  int local_14;
  uint local_10;
  uint local_c;
  int local_8;

  uVar3 = 0;
  local_18 = 0;
  local_c = CFastVB__CountNodeTreeExpandedLeafCount(this,(int)param_1,unaff_EDI);
  local_10 = CFastVB__CountNodeTreeExpandedLeafCount(this,(int)param_2,unaff_EDI);
  bVar1 = CFastVB__AreNodeTreesStructurallyEqual((int)param_1,(int)param_2);
  if (CONCAT31(extraout_var,bVar1) == 0) {
    bVar1 = false;
    local_8 = 0;
    CFastVB__InitNodeType9(local_60);
    CFastVB__InitNodeType9(local_3c);
    if (local_c != 0) {
      while (uVar3 < local_10) {
        iVar2 = CFastVB__FlattenNodeTreeLeafByLinearIndex
                          (this,param_1,uVar3,(uint)local_60,unaff_EBX);
        if (((iVar2 < 0) ||
            (iVar2 = CFastVB__FlattenNodeTreeLeafByLinearIndex
                               (this,param_2,uVar3,(uint)local_3c,unaff_EBX), iVar2 < 0)) ||
           (iVar2 = CFastVB__ResolveCommonLeafFormat((int)local_60,(int)local_3c,&local_14),
           iVar2 < 0)) {
          bVar1 = true;
          local_8 = 1;
        }
        else {
          if (local_14 != local_4c) {
            bVar1 = true;
          }
          if (local_14 != local_28) {
            local_8 = 1;
          }
        }
        if (((bVar1) && (local_8 != 0)) || (uVar3 = uVar3 + 1, local_c <= uVar3)) break;
      }
    }
    iVar2 = local_18;
    if (local_10 < local_c) {
      iVar2 = 4;
    }
    if (bVar1) {
      iVar2 = iVar2 + 0x200;
    }
    if (local_8 != 0) {
      iVar2 = iVar2 + 0x10000;
    }
    if (local_c < local_10) {
      iVar2 = iVar2 + 0x800000;
    }
    CFastVB__NodeType9__dtor(local_3c);
    CFastVB__NodeType9__dtor(local_60);
  }
  else {
    iVar2 = 0;
  }
  return iVar2;
}
