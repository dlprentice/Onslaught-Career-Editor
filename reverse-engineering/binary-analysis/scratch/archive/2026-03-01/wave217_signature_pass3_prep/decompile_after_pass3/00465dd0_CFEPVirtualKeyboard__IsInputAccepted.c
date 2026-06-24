/* address: 0x00465dd0 */
/* name: CFEPVirtualKeyboard__IsInputAccepted */
/* signature: int __thiscall CFEPVirtualKeyboard__IsInputAccepted(void * this, void * input_ctx, int key_code) */


int __thiscall CFEPVirtualKeyboard__IsInputAccepted(void *this,void *input_ctx,int key_code)

{
  uint uVar1;

  if (*(char *)((int)this + 0x15c) != '\0') {
    return 1;
  }
  uVar1 = (*(code *)**(undefined4 **)this)(input_ctx);
  return (uint)(uVar1 != (DAT_00679af4 & 0xff));
}
