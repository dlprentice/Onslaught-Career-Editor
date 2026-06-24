/* address: 0x0044a6e0 */
/* name: CResourceAccumulator__Helper_0044a6e0 */
/* signature: void __stdcall CResourceAccumulator__Helper_0044a6e0(void * param_1) */


void CResourceAccumulator__Helper_0044a6e0(void *param_1)

{
  void *this;
  void *unaff_ESI;
  int iVar1;

  this = param_1;
  CMeshPart__Helper_00423910((uint)param_1);
  CMeshPart__Helper_00423960(this,(int)&param_1,4,1,(int)unaff_ESI);
  iVar1 = 0;
  if (0 < (int)param_1) {
    do {
      CMapTex__Deserialize(this,iVar1);
      iVar1 = iVar1 + 1;
    } while (iVar1 < (int)param_1);
  }
  CResourceAccumulator__Helper_00491060(&DAT_006fadc8,(int)this,unaff_ESI);
  return;
}
