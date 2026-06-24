/* address: 0x004bb040 */
/* name: CMeshPart__CanMergeInOptimizePass */
/* signature: int __cdecl CMeshPart__CanMergeInOptimizePass(int param_1) */


int __cdecl CMeshPart__CanMergeInOptimizePass(int param_1)

{
  bool bVar1;
  undefined3 extraout_var;
  undefined3 extraout_var_00;
  int iVar2;
  undefined3 extraout_var_01;
  undefined3 extraout_var_02;
  undefined3 extraout_var_03;
  undefined3 extraout_var_04;
  undefined3 extraout_var_05;
  undefined3 extraout_var_06;
  undefined3 extraout_var_07;
  undefined3 extraout_var_08;
  undefined3 extraout_var_09;
  undefined3 extraout_var_10;

  bVar1 = CMeshPart__Helper_00494b50();
  if (CONCAT31(extraout_var,bVar1) != 0) {
    bVar1 = CMeshPart__Helper_00494b00(param_1);
    if (CONCAT31(extraout_var_00,bVar1) == 0) {
      return 0;
    }
  }
  iVar2 = CMeshPart__Helper_004950f0(*(int *)(param_1 + 0x128));
  if (iVar2 != 0) {
    iVar2 = CMCBuggy__Unk_00495090(param_1);
    if (iVar2 == 0) {
      return 0;
    }
  }
  iVar2 = CMeshPart__Helper_004957d0(*(int *)(param_1 + 0x128));
  if (iVar2 != 0) {
    bVar1 = CMeshPart__Helper_00496f60(param_1);
    if (CONCAT31(extraout_var_01,bVar1) == 0) {
      return 0;
    }
  }
  iVar2 = CMeshPart__Helper_004957d0(*(int *)(param_1 + 0x128));
  if (iVar2 != 0) {
    iVar2 = CFrontEndPage__Init_ReturnTrue();
    if (iVar2 == 0) {
      return 0;
    }
  }
  bVar1 = CMeshPart__Helper_00496270();
  if (CONCAT31(extraout_var_02,bVar1) != 0) {
    iVar2 = CFrontEndPage__Init_ReturnTrue();
    if (iVar2 == 0) {
      return 0;
    }
  }
  bVar1 = CMeshPart__Helper_0049c2d0();
  if (CONCAT31(extraout_var_03,bVar1) != 0) {
    bVar1 = CMeshPart__Helper_0049c250(param_1);
    if (CONCAT31(extraout_var_04,bVar1) == 0) {
      return 0;
    }
  }
  iVar2 = CMeshPart__Helper_00496910(*(int *)(param_1 + 0x128));
  if (iVar2 != 0) {
    iVar2 = CFrontEndPage__Init_ReturnTrue();
    if (iVar2 == 0) {
      return 0;
    }
  }
  iVar2 = CMeshPart__Helper_004957d0(*(int *)(param_1 + 0x128));
  if (iVar2 != 0) {
    bVar1 = CMeshPart__Helper_00496f60(param_1);
    if (CONCAT31(extraout_var_05,bVar1) == 0) {
      return 0;
    }
  }
  iVar2 = CMCMech__HasCylinderBones(*(undefined4 *)(param_1 + 0x128));
  if (iVar2 != 0) {
    iVar2 = CMCMech__HasAllCylinders(param_1);
    if (iVar2 == 0) {
      return 0;
    }
  }
  bVar1 = CMeshPart__Helper_0049c2d0();
  if (CONCAT31(extraout_var_06,bVar1) != 0) {
    bVar1 = CMeshPart__Helper_0049c250(param_1);
    if (CONCAT31(extraout_var_07,bVar1) == 0) {
      return 0;
    }
  }
  iVar2 = CMCTentacle__HasTentacleBone(*(undefined4 *)(param_1 + 0x128));
  if (iVar2 != 0) {
    iVar2 = CMCTentacle__ValidateBoneStructure(param_1);
    if (iVar2 == 0) {
      return 0;
    }
  }
  bVar1 = CMeshPart__Helper_0049c2d0();
  if (CONCAT31(extraout_var_08,bVar1) != 0) {
    bVar1 = CMeshPart__Helper_0049c250(param_1);
    if (CONCAT31(extraout_var_09,bVar1) == 0) {
      return 0;
    }
  }
  iVar2 = CMeshPart__Helper_0049f670(*(int *)(param_1 + 0x128));
  if (iVar2 != 0) {
    bVar1 = CMeshPart__Helper_0049f600(param_1);
    if (CONCAT31(extraout_var_10,bVar1) == 0) {
      return 0;
    }
  }
  return 1;
}
