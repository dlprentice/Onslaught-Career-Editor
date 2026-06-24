/* address: 0x00465dd0 */
/* name: CUnitAI__Unk_00465dd0 */
/* signature: bool __thiscall CUnitAI__Unk_00465dd0(void * this, void * param_1, int param_2) */


bool __thiscall CUnitAI__Unk_00465dd0(void *this,void *param_1,int param_2)

{
  uint uVar1;

  if (*(char *)((int)this + 0x15c) != '\0') {
    return true;
  }
  uVar1 = (*(code *)**(undefined4 **)this)(param_1);
  return uVar1 != (DAT_00679af4 & 0xff);
}
