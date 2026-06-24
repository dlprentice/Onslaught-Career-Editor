/* address: 0x004a5200 */
/* name: CMesh__InitStatic */
/* signature: undefined CMesh__InitStatic(void) */


undefined4 CMesh__InitStatic(void)

{
  void *obj;
  int iVar1;
  undefined4 *extraout_EAX;
  int *piVar2;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  obj = DAT_00704adc;
  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d3709;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  if (DAT_00704adc != (void *)0x0) {
    ExceptionList = &local_c;
    CExplosionInitThing__Unk_004adf90(DAT_00704adc);
    OID__FreeObject(obj);
  }
  iVar1 = OID__AllocObject(0x24,0x24,s_C__dev_ONSLAUGHT2_mesh_cpp_0062f8e8,0x91);
  local_4 = 0;
  if (iVar1 == 0) {
    DAT_00704adc = (undefined4 *)0x0;
  }
  else {
    CInfluenceMap__Unk_004adf80(iVar1);
    DAT_00704adc = extraout_EAX;
  }
  local_4 = 0xffffffff;
  CMeshPart__Unk_004ae080(DAT_00704adc);
  piVar2 = CTexture__FindTexture(s_meshtex_default_tga_00625498,0,0,-1,1,1);
  *DAT_00704adc = piVar2;
  ExceptionList = local_c;
  return 1;
}
