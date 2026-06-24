/* address: 0x00480a30 */
/* name: CUnitAI__Unk_00480a30 */
/* signature: void __thiscall CUnitAI__Unk_00480a30(void * this, int param_1, int param_2) */


void __thiscall CUnitAI__Unk_00480a30(void *this,int param_1,int param_2)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int extraout_EAX;
  int *piVar7;
  int extraout_EAX_00;
  int iVar8;
  int iVar9;
  void *unaff_ESI;
  short local_10;
  short local_e;
  int local_c;
  short local_8;
  short local_6;

  *(int *)((int)this + 8) = param_1;
  *(undefined4 *)((int)this + 0x10) = 0;
  *(undefined4 *)((int)this + 0xc) = 0;
  if (*(int *)(*(int *)(param_1 + 8) + 0x18) == -1) {
    iVar3 = 0;
  }
  else {
    iVar3 = *(int *)(param_1 + 8) + 0xc;
  }
  iVar3 = *(int *)(iVar3 + 0xc);
  for (iVar9 = iVar3; -1 < iVar9; iVar9 = iVar9 + -1) {
    CMapWho__WorldToSector(&local_8,*(int *)(*(int *)((int)this + 8) + 8) + 0x1c,iVar9);
    iVar8 = (int)local_6;
    iVar4 = (int)local_8;
    for (iVar5 = iVar4 + -1; iVar2 = iVar8 + -1, iVar5 <= iVar4 + 1; iVar5 = iVar5 + 1) {
      for (; iVar2 <= iVar8 + 1; iVar2 = iVar2 + 1) {
        local_10 = (short)iVar5;
        local_e = (short)iVar2;
        local_c = iVar9;
        iVar6 = CMapWho__Unk_00491da0(&local_10);
        if (iVar6 != 0) {
          piVar7 = (int *)(*(int *)(DAT_00704290 + local_c * 4) +
                          ((0x40 >> (4U - (char)local_c & 0x1f)) * (int)local_e + (int)local_10) * 8
                          );
          if (iVar3 == iVar9) {
            piVar1 = (int *)*piVar7;
            if (piVar1 != (int *)0x0) {
              CUnitAI__Unk_00480e10(this,*piVar1,unaff_ESI);
              CUnitAI__Unk_00480e10(this,piVar1[1],unaff_ESI);
              CUnitAI__Unk_00480e10(this,piVar1[2],unaff_ESI);
              CUnitAI__Unk_00480e10(this,piVar1[3],unaff_ESI);
            }
            CMapWho__Unk_00491d80(&DAT_00704200,piVar7,(int)unaff_ESI);
            iVar6 = extraout_EAX;
            while (iVar6 != 0) {
              iVar6 = CMapWhoEntry__GetOwner();
              piVar7 = (int *)CThing__Unk_004f3d10(iVar6);
              if (((piVar7 != (int *)0x0) && (piVar7 != *(int **)((int)this + 8))) &&
                 ((iVar6 = (**(code **)(**(int **)((int)this + 8) + 0x20))(piVar7), iVar6 != 0 &&
                  (iVar6 = (**(code **)(*piVar7 + 0x20))(*(undefined4 *)((int)this + 8)), iVar6 != 0
                  )))) {
                if (*(int *)((int)this + 0x10) == 1) {
                  CConsole__Printf(&DAT_0066f580,s_WARNING__Unexpected_collision_ch_0062cdec);
                }
                else {
                  CUnitAI__Helper_00480ed0(this,piVar7,unaff_ESI);
                  *(undefined4 *)((int)this + 0x10) = 0;
                }
              }
              iVar6 = CMapWho__Unk_00491d90(&DAT_00704200);
            }
          }
          else {
            CMapWho__Unk_00491d80(&DAT_00704200,piVar7,(int)unaff_ESI);
            iVar6 = extraout_EAX_00;
            while (iVar6 != 0) {
              iVar6 = CMapWhoEntry__GetOwner();
              piVar7 = (int *)CThing__Unk_004f3d10(iVar6);
              if ((((piVar7 != (int *)0x0) && (piVar7 != *(int **)((int)this + 8))) &&
                  (iVar6 = (**(code **)(**(int **)((int)this + 8) + 0x20))(piVar7), iVar6 != 0)) &&
                 (iVar6 = (**(code **)(*piVar7 + 0x20))(*(undefined4 *)((int)this + 8)), iVar6 != 0)
                 ) {
                if (*(int *)((int)this + 0x10) == 1) {
                  CConsole__Printf(&DAT_0066f580,s_WARNING__Unexpected_collision_ch_0062cdec);
                }
                else {
                  CUnitAI__Helper_00480ed0(this,piVar7,unaff_ESI);
                  *(undefined4 *)((int)this + 0x10) = 0;
                }
              }
              iVar6 = CMapWho__Unk_00491d90(&DAT_00704200);
            }
          }
        }
      }
    }
  }
  return;
}
