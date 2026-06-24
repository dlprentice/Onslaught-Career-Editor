/* address: 0x005042f0 */
/* name: CResourceAccumulator__InitVertexShaderPrograms */
/* signature: void __cdecl CResourceAccumulator__InitVertexShaderPrograms(void * param_1) */


void __cdecl CResourceAccumulator__InitVertexShaderPrograms(void *param_1)

{
  void *this;
  undefined **ppuVar1;
  int iVar2;
  int unaff_EDI;
  undefined4 local_4;

  this = param_1;
  CMeshPart__Helper_00423960(param_1,(int)&local_4,4,1,unaff_EDI);
  CMeshPart__Helper_00423960(this,(int)&param_1,4,1,unaff_EDI);
  CMeshPart__Helper_00423960(this,0x634070,0x4e0,1,unaff_EDI);
  ppuVar1 = &PTR_s_f_create_eyespace_vertex_00634074;
  do {
    *ppuVar1 = (undefined *)0x0;
    ppuVar1 = ppuVar1 + 3;
  } while (ppuVar1 < &DAT_00634554);
  iVar2 = 0;
  DAT_00854e74 = local_4;
  if (0 < (int)param_1) {
    do {
      CVertexShader__Clone(this,iVar2);
      iVar2 = iVar2 + 1;
    } while (iVar2 < (int)param_1);
  }
  return;
}
