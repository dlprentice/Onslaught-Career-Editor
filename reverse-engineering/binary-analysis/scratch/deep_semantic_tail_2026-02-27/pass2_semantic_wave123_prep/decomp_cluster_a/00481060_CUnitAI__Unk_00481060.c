/* address: 0x00481060 */
/* name: CUnitAI__Unk_00481060 */
/* signature: void __thiscall CUnitAI__Unk_00481060(void * this, void * param_1, void * param_2, void * param_3) */


void __thiscall CUnitAI__Unk_00481060(void *this,void *param_1,void *param_2,void *param_3)

{
  int *piVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  int extraout_EAX;
  int extraout_EAX_00;
  int *piVar6;
  int iVar7;
  uint uVar8;
  void *unaff_EDI;
  int local_24;
  int local_20;
  short local_1c;
  undefined4 local_18;
  int local_14;
  undefined4 local_10;
  int local_c;
  short local_8;
  short local_6;
  int local_4;

  local_c = *(int *)((int)param_1 + 4);
  iVar7 = *(int *)((int)param_2 + 4);
  uVar3 = *(undefined4 *)param_1;
  local_14 = iVar7;
  uVar2 = *(undefined4 *)param_2;
  for (; -1 < iVar7; iVar7 = iVar7 + -1) {
    local_18._0_2_ = (short)uVar2;
    local_10._0_2_ = (short)uVar3;
    local_18._2_2_ = (short)((uint)uVar2 >> 0x10);
    local_10._2_2_ = (short)((uint)uVar3 >> 0x10);
    if ((((short)local_18 != (short)local_10) || (local_18._2_2_ != local_10._2_2_)) ||
       (local_14 != local_c)) {
      local_20 = -1;
      do {
        local_1c = (short)local_20 + (short)local_18;
        local_24 = -1;
        do {
          local_8 = local_1c;
          local_6 = (short)local_24 + local_18._2_2_;
          local_4 = iVar7;
          iVar4 = CMapWho__IsEntryInBounds(&local_8);
          if ((iVar4 != 0) &&
             ((uVar5 = (int)local_8 - (int)(short)local_10, uVar8 = (int)uVar5 >> 0x1f,
              1 < (int)((uVar5 ^ uVar8) - uVar8) ||
              (uVar5 = (int)local_6 - (int)local_10._2_2_ >> 0x1f,
              1 < (int)(((int)local_6 - (int)local_10._2_2_ ^ uVar5) - uVar5))))) {
            piVar6 = (int *)(*(int *)(DAT_00704290 + local_4 * 4) +
                            ((0x40 >> (4U - (char)local_4 & 0x1f)) * (int)local_6 + (int)local_8) *
                            8);
            if (iVar7 == *(int *)((int)param_2 + 4)) {
              piVar1 = (int *)*piVar6;
              if (piVar1 != (int *)0x0) {
                CCollisionSeekingRound__Helper_00480e10(this,*piVar1,unaff_EDI);
                CCollisionSeekingRound__Helper_00480e10(this,piVar1[1],unaff_EDI);
                CCollisionSeekingRound__Helper_00480e10(this,piVar1[2],unaff_EDI);
                CCollisionSeekingRound__Helper_00480e10(this,piVar1[3],unaff_EDI);
              }
              CCollisionSeekingRound__Helper_00491d80(&DAT_00704200,piVar6,(int)unaff_EDI);
              iVar4 = extraout_EAX;
              while (iVar4 != 0) {
                iVar4 = CMapWhoEntry__GetOwner();
                iVar4 = CCollisionSeekingRound__Helper_004f3d10(iVar4);
                if (iVar4 != 0) {
                  CUnitAI__Unk_00480db0(this,iVar4,unaff_EDI);
                }
                iVar4 = CCollisionSeekingRound__Helper_00491d90(&DAT_00704200);
              }
            }
            else {
              CCollisionSeekingRound__Helper_00491d80(&DAT_00704200,piVar6,(int)unaff_EDI);
              iVar4 = extraout_EAX_00;
              while (iVar4 != 0) {
                iVar4 = CMapWhoEntry__GetOwner();
                piVar6 = (int *)CCollisionSeekingRound__Helper_004f3d10(iVar4);
                if (((piVar6 != (int *)0x0) && (piVar6 != *(int **)((int)this + 8))) &&
                   ((iVar4 = (**(code **)(**(int **)((int)this + 8) + 0x20))(piVar6), iVar4 != 0 &&
                    (iVar4 = (**(code **)(*piVar6 + 0x20))(*(undefined4 *)((int)this + 8)),
                    iVar4 != 0)))) {
                  if (*(int *)((int)this + 0x10) == 1) {
                    CConsole__Printf(&DAT_0066f580,s_WARNING__Unexpected_collision_ch_0062cdec);
                  }
                  else {
                    CUnitAI__Helper_00480ed0(this,piVar6,unaff_EDI);
                    *(undefined4 *)((int)this + 0x10) = 0;
                  }
                }
                iVar4 = CCollisionSeekingRound__Helper_00491d90(&DAT_00704200);
              }
            }
          }
          local_24 = local_24 + 1;
        } while (local_24 < 2);
        local_20 = local_20 + 1;
      } while (local_20 < 2);
    }
    if (iVar7 != 0) {
      local_18 = CONCAT22(local_18._2_2_ >> 1,(short)local_18 >> 1);
      local_14 = local_14 + -1;
      local_c = local_c + -1;
      local_10 = CONCAT22(local_10._2_2_ >> 1,(short)local_10 >> 1);
      uVar2 = local_18;
      uVar3 = local_10;
    }
    local_10 = uVar3;
    local_18 = uVar2;
    uVar3 = local_10;
    uVar2 = local_18;
  }
  return;
}
