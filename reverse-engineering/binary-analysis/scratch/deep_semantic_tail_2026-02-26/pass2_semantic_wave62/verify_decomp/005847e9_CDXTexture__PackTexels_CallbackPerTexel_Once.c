/* address: 0x005847e9 */
/* name: CDXTexture__PackTexels_CallbackPerTexel_Once */
/* signature: void __thiscall CDXTexture__PackTexels_CallbackPerTexel_Once(void * this, void * param_1, int param_2, int param_3, int param_4) */


void __thiscall
CDXTexture__PackTexels_CallbackPerTexel_Once
          (void *this,void *param_1,int param_2,int param_3,int param_4)

{
  int unaff_ESI;

  if (*(int *)((int)this + 0x10) != 0) {
    CDXTexture__Helper_00581e8c(this,param_3,unaff_ESI);
  }
  CDXTexture__Helper_005759c3();
  return;
}
