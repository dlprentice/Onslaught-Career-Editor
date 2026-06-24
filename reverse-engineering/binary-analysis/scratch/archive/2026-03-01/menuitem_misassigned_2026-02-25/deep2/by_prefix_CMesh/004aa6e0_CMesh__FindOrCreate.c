/* address: 0x004aa6e0 */
/* name: CMesh__FindOrCreate */
/* signature: undefined CMesh__FindOrCreate(void) */


void * CMesh__FindOrCreate(char *param_1,void *param_2)

{
  void **ppvVar1;
  int iVar2;
  void *this;
  int unaff_EDI;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d3889;
  ppvVar1 = &local_c;
  local_c = ExceptionList;
  for (this = DAT_00704ad8; ExceptionList = ppvVar1, this != (void *)0x0;
      this = *(void **)((int)this + 0x158)) {
    iVar2 = stricmp(param_1,(char *)((int)this + 0x24));
    if (iVar2 == 0) goto LAB_004aa791;
    ppvVar1 = ExceptionList;
  }
  iVar2 = OID__AllocObject(0x174,1,s_C__dev_ONSLAUGHT2_mesh_cpp_0062f8e8,0x755);
  local_4 = 0;
  if (iVar2 == 0) {
    this = (void *)0x0;
  }
  else {
    this = (void *)CMesh__Init();
  }
  local_4 = 0xffffffff;
  if (this != (void *)0x0) {
    iVar2 = CMesh__Unk_004a5970(this,(int)param_1,param_2,unaff_EDI);
    if (iVar2 != 0) {
      if (DAT_00704ae0 != 0) {
        CConsole__Printf(&DAT_0066f580,s_Mesh___s__not_found_in_level_res_0062fc80);
      }
LAB_004aa791:
      *(int *)((int)this + 0x170) = *(int *)((int)this + 0x170) + 1;
      ExceptionList = local_c;
      return this;
    }
    CMesh__Unk_004a50b0(this);
    OID__FreeObject(this);
  }
  ExceptionList = local_c;
  return (void *)0x0;
}
