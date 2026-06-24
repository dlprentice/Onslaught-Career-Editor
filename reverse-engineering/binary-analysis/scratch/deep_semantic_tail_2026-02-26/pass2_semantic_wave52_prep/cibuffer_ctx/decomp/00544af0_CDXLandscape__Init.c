/* address: 0x00544af0 */
/* name: CDXLandscape__Init */
/* signature: undefined CDXLandscape__Init(void) */


undefined4 __fastcall CDXLandscape__Init(int *param_1)

{
  undefined4 uVar1;
  int iVar2;
  void *pvVar3;
  int unaff_ESI;
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d7a0b;
  pvStack_c = ExceptionList;
  ExceptionList = &pvStack_c;
  CLandscapeTexture__ResetUpdateQueue();
  param_1[8] = 0;
  uVar1 = DAT_00889010;
  DAT_00889010 = 1;
  CDamage__Init();
  CConsole__RegisterCommand
            (s_BuildLandscapeCache_00650dc4,s_Build_the_landscape_texture_cach_00650dd8,
             &LAB_00544700,0);
  CConsole__RegisterVariable
            (s_xx_coastcalc_00650d98,s_coast_calculation_thingy_00650da8,3,&DAT_008aa938,0,0);
  iVar2 = OID__AllocObject(0x50,2,s_C__dev_ONSLAUGHT2_DXLandscape_cp_00650bdc,0xa9);
  local_4 = 0;
  if (iVar2 == 0) {
    iVar2 = 0;
  }
  else {
    iVar2 = CLandscapeTexture__ConstructorMip();
  }
  local_4 = 0xffffffff;
  param_1[0xc] = iVar2;
  CLandscapeTexture__Init(0,4);
  pvVar3 = (void *)OID__AllocObject(0x2c,0x35,s_C__dev_ONSLAUGHT2_DXLandscape_cp_00650bdc,0xae);
  local_4 = 1;
  if (pvVar3 == (void *)0x0) {
    iVar2 = 0;
  }
  else {
    iVar2 = CVBuffer__ctor_like_004fff00(pvVar3);
  }
  local_4 = 0xffffffff;
  param_1[10] = iVar2;
  CVBuffer__Create(0x1081,0x14,0x102);
  iVar2 = OID__AllocObject(0x24,0x35,s_C__dev_ONSLAUGHT2_DXLandscape_cp_00650bdc,0xb3);
  local_4 = 2;
  if (iVar2 == 0) {
    pvVar3 = (void *)0x0;
  }
  else {
    pvVar3 = (void *)CIBuffer__Constructor();
  }
  local_4 = 0xffffffff;
  param_1[0xb] = (int)pvVar3;
  CIBuffer__Unk_00488330(pvVar3,(void *)0x9c40,0x208,0x65,0,unaff_ESI);
  DAT_00889010 = uVar1;
  CShaderBase__Init((int)param_1);
  (**(code **)(*param_1 + 4))();
  if (((param_1[7] != 0) && (param_1[2] != 0)) && (param_1[3] != 0)) {
    iVar2 = CVertexShader__Create
                      (s_LandscapeShader_00650c3c,s_vs_1_1_dcl_position_v0_dcl_texco_00650c4c,4,0,0,
                       0xffffffff);
    param_1[6] = iVar2;
  }
  ExceptionList = pvStack_c;
  return 1;
}
