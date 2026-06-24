/* address: 0x00584786 */
/* name: CDXTexture__PackTexels_CallbackPerTexel_RepeatB */
/* signature: void __thiscall CDXTexture__PackTexels_CallbackPerTexel_RepeatB(void * this, void * param_1, int param_2, int param_3, int param_4) */


void __thiscall
CDXTexture__PackTexels_CallbackPerTexel_RepeatB
          (void *this,void *param_1,int param_2,int param_3,int param_4)

{
  uint uVar1;
  int unaff_EDI;

  uVar1 = 0;
  if (*(int *)((int)this + 0x10) != 0) {
    CDXTexture__Helper_00581e8c(this,param_3,unaff_EDI);
  }
  if (*(int *)((int)this + 0x1060) != 0) {
    do {
      CDXTexture__Helper_005759c3();
      uVar1 = uVar1 + 1;
    } while (uVar1 < *(uint *)((int)this + 0x1060));
  }
  return;
}
