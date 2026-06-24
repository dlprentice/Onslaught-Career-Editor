/* address: 0x00568797 */
/* name: CDXTexture__Unk_00568797 */
/* signature: int __thiscall CDXTexture__Unk_00568797(void * this, int param_1, double param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall CDXTexture__Unk_00568797(void *this,int param_1,double param_2)

{
  uint uVar1;
  float10 fVar2;
  uint in_stack_00000008;
  int iVar3;
  undefined8 uVar4;

  uVar4 = CONCAT44(this,this);
  uVar1 = CRT__ClassifyDoubleWords(param_1,in_stack_00000008);
  if ((uVar1 & 0x90) == 0) {
    fVar2 = (float10)__frnd(_param_1,uVar4);
    if ((double)fVar2 == _param_1) {
      _param_1 = _param_1 / _DAT_005db488;
      fVar2 = (float10)__frnd();
      if (fVar2 == (float10)_param_1) {
        iVar3 = 2;
      }
      else {
        iVar3 = 1;
      }
      return iVar3;
    }
  }
  return 0;
}
