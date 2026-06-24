/* address: 0x0057457a */
/* name: CDXTexture__LoadAndUploadMappedTexture_0057457a */
/* signature: int __stdcall CDXTexture__LoadAndUploadMappedTexture_0057457a(void * param_1, void * param_2, void * param_3, void * param_4, void * param_5) */


int CDXTexture__LoadAndUploadMappedTexture_0057457a
              (void *param_1,void *param_2,void *param_3,void *param_4,void *param_5)

{
  int *in_EAX;
  void *unaff_ESI;
  int iVar1;
  undefined1 local_dc [80];
  undefined1 local_8c [96];
  int local_2c;
  undefined1 local_18 [20];

  CDXTexture__InitSurfaceNodeZeroed(local_8c);
  CDXTexture__ResetSurfaceCopyContext(local_18);
  if ((param_1 == (void *)0x0) || (in_EAX == (int *)0x0)) {
    iVar1 = -0x7789f794;
  }
  else {
    iVar1 = CDXTexture__UploadSurfaceRegionWithFallback();
    if (((-1 < iVar1) &&
        (iVar1 = CTexture__Helper_00579d33(local_8c,local_dc,unaff_ESI), -1 < iVar1)) &&
       (iVar1 = CMeshCollisionVolume__LoadMappedTextureResourcesByMode
                          (local_8c,param_1,(int)param_2,(int)param_5,(int)unaff_ESI), -1 < iVar1))
    {
      (**(code **)(*in_EAX + 0x30))();
      if (local_2c == 0) {
        (**(code **)(*in_EAX + 0xc))();
        iVar1 = (**(code **)(*(int *)param_1 + 0xc))(param_1);
        (**(code **)(*(int *)param_1 + 8))(param_1);
        if (iVar1 != 0) {
          iVar1 = -0x7789f798;
          goto LAB_0057462b;
        }
      }
      iVar1 = 0;
    }
  }
LAB_0057462b:
  CDXTexture__FinalizeTextureUploadAndReleaseTemp_Duplicate(local_18);
  CDXTexture__FreeSurfaceNodeTree((int)local_8c);
  return iVar1;
}
