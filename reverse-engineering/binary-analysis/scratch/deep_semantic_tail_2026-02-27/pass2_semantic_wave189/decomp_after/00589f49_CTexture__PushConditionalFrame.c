/* address: 0x00589f49 */
/* name: CTexture__PushConditionalFrame */
/* signature: int __thiscall CTexture__PushConditionalFrame(void * this, int param_1, void * param_2) */


int __thiscall CTexture__PushConditionalFrame(void *this,int param_1,void *param_2)

{
  void *this_00;
  int extraout_EAX;
  int iVar1;
  undefined4 uVar2;
  int unaff_ESI;

  OID__AllocObject_DefaultTag_00662b2c(0x10);
  if (this_00 == (void *)0x0) {
    iVar1 = 0;
  }
  else {
    CTexture__IncludeNodeCtor(this_00,(void *)param_1,*(int *)((int)this + 0x38),unaff_ESI);
    iVar1 = extraout_EAX;
  }
  if (iVar1 == 0) {
    iVar1 = -0x7ff8fff2;
  }
  else {
    *(undefined4 *)(iVar1 + 0xc) = *(undefined4 *)(*(int *)((int)this + 0x50) + 0x38);
    *(int *)(*(int *)((int)this + 0x50) + 0x38) = iVar1;
    if ((*(int *)((int)this + 0x38) == 0) || (param_1 == 0)) {
      uVar2 = 0;
    }
    else {
      uVar2 = 1;
    }
    *(undefined4 *)((int)this + 0x3c) = uVar2;
    iVar1 = 0;
  }
  return iVar1;
}
