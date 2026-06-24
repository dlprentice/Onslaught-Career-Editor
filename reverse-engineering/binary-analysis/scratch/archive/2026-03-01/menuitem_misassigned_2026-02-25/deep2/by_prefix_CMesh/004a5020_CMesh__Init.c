/* address: 0x004a5020 */
/* name: CMesh__Init */
/* signature: undefined CMesh__Init(void) */


undefined4 * __fastcall CMesh__Init(undefined4 *param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 *puVar3;

  param_1[0x57] = 0;
  param_1[0x58] = 0;
  param_1[7] = 0;
  param_1[8] = 0;
  param_1[5] = 0;
  param_1[6] = 0;
  param_1[1] = 0;
  *param_1 = 0;
  param_1[0x59] = 0x3f000000;
  param_1[0x5b] = 0xfffffffe;
  param_1[2] = 0;
  param_1[4] = 0;
  param_1[3] = 0;
  param_1[0x5c] = 0;
  param_1[0x55] = 0xffffffff;
  puVar3 = param_1 + 9;
  for (iVar2 = 0x4b; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar3 = 0;
    puVar3 = puVar3 + 1;
  }
  uVar1 = OID__AllocObject(0x28,1,s_C__dev_ONSLAUGHT2_mesh_cpp_0062f8e8,0x3d);
  param_1[0x54] = uVar1;
  param_1[0x56] = DAT_00704ad8;
  DAT_00704ad8 = param_1;
  return param_1;
}
