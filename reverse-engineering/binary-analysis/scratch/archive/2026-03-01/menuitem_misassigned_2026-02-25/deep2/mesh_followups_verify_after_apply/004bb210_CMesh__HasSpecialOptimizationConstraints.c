/* address: 0x004bb210 */
/* name: CMesh__HasSpecialOptimizationConstraints */
/* signature: bool __cdecl CMesh__HasSpecialOptimizationConstraints(int param_1) */


bool __cdecl CMesh__HasSpecialOptimizationConstraints(int param_1)

{
  bool bVar1;
  undefined3 extraout_var;
  undefined3 extraout_var_00;
  undefined3 extraout_var_01;
  int iVar2;
  undefined3 extraout_var_02;

  bVar1 = CMCBuggy__Unk_00494b50();
  if (CONCAT31(extraout_var,bVar1) != 0) {
    return true;
  }
  bVar1 = CUnitAI__Unk_0049c2d0();
  if (CONCAT31(extraout_var_00,bVar1) != 0) {
    return true;
  }
  bVar1 = CUnitAI__Unk_0049c2d0();
  if (CONCAT31(extraout_var_01,bVar1) != 0) {
    return true;
  }
  iVar2 = CMCMech__HasCylinderBones(param_1);
  if (iVar2 != 0) {
    return true;
  }
  iVar2 = CMCTentacle__HasTentacleBone(param_1);
  if (iVar2 != 0) {
    return true;
  }
  bVar1 = CUnitAI__Unk_0049c2d0();
  return CONCAT31(extraout_var_02,bVar1) != 0;
}
