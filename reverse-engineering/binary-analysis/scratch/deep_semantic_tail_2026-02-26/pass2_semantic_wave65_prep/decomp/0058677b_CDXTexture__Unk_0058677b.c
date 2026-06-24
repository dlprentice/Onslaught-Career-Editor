/* address: 0x0058677b */
/* name: CDXTexture__Unk_0058677b */
/* signature: void __thiscall CDXTexture__Unk_0058677b(void * this, void * param_1, int param_2, int param_3, uint param_4) */


void __thiscall
CDXTexture__Unk_0058677b(void *this,void *param_1,int param_2,int param_3,uint param_4)

{
  uint uVar1;

  uVar1 = param_3;
  CDXTexture__Helper_00575a65();
  if (*(int *)((int)this + 0x18) != 0) {
    CFastVB__Helper_00581e1c(this,param_3,uVar1);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    CTexture__Helper_0058210e(this,param_3,uVar1);
  }
  return;
}
