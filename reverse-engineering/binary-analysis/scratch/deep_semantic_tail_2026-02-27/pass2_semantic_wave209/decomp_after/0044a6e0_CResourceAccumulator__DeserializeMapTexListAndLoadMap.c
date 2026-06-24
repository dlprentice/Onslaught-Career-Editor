/* address: 0x0044a6e0 */
/* name: CResourceAccumulator__DeserializeMapTexListAndLoadMap */
/* signature: void __stdcall CResourceAccumulator__DeserializeMapTexListAndLoadMap(void * param_1) */


void CResourceAccumulator__DeserializeMapTexListAndLoadMap(void *param_1)

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
  CResourceAccumulator__DeserializeMapAndInitResources(&DAT_006fadc8,(int)this,unaff_ESI);
  return;
}
