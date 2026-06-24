/* address: 0x00589802 */
/* name: CTexture__PushPreprocessorStateNode */
/* signature: int __thiscall CTexture__PushPreprocessorStateNode(void * this, int param_1, int param_2) */


int __thiscall CTexture__PushPreprocessorStateNode(void *this,int param_1,int param_2)

{
  int *extraout_EAX;
  int *piVar1;
  int iVar2;

  OID__AllocObject_DefaultTag_00662b2c(0xc);
  if (extraout_EAX == (int *)0x0) {
    piVar1 = (int *)0x0;
  }
  else {
    extraout_EAX[1] = 0;
    *extraout_EAX = param_1;
    extraout_EAX[2] = 1;
    piVar1 = extraout_EAX;
  }
  if (piVar1 == (int *)0x0) {
    iVar2 = -0x7ff8fff2;
  }
  else {
    piVar1[1] = *(int *)((int)this + 0x48);
    *(int **)((int)this + 0x48) = piVar1;
    *(int *)((int)this + 0x80) = param_1;
    iVar2 = 0;
  }
  return iVar2;
}
