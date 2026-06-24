/* address: 0x00465dd0 */
/* name: CFEPVirtualKeyboard__IsInputAccepted */
/* signature: bool __thiscall CFEPVirtualKeyboard__IsInputAccepted(void * this, void * param_1, int param_2) */


bool __thiscall CFEPVirtualKeyboard__IsInputAccepted(void *this,void *param_1,int param_2)

{
  uint uVar1;

  if (*(char *)((int)this + 0x15c) != '\0') {
    return true;
  }
  uVar1 = (*(code *)**(undefined4 **)this)(param_1);
  return uVar1 != (DAT_00679af4 & 0xff);
}
