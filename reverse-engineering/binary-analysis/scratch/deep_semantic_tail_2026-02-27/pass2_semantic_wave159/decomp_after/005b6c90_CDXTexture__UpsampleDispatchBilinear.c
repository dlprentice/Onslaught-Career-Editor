/* address: 0x005b6c90 */
/* name: CDXTexture__UpsampleDispatchBilinear */
/* signature: void __stdcall CDXTexture__UpsampleDispatchBilinear(void * param_1, int param_2, void * param_3, int param_4) */


void CDXTexture__UpsampleDispatchBilinear(void *param_1,int param_2,void *param_3,int param_4)

{
  int iVar1;

  if ((*(byte *)param_3 & 7) == 0) {
    if ((*(int *)((int)param_1 + 0xc4) == 5) || (*(int *)((int)param_1 + 0xc4) == 6)) {
      CDXTexture__UpsampleBilinear2x2_Sse(param_2,(int)param_1,(int)param_3,param_4);
      return;
    }
  }
  else {
    iVar1 = *(int *)param_1;
    *(undefined4 *)(iVar1 + 0x14) = 2;
    (**(code **)(iVar1 + 4))(param_1,0xffffffff);
  }
  CDXTexture__UpsampleBilinear2x2_Scalar(param_3,param_2,param_4);
  return;
}
