/* address: 0x00420cd0 */
/* name: CCareer__Unk_00420cd0 */
/* signature: int __thiscall CCareer__Unk_00420cd0(void * this, int param_1, int param_2) */


int __thiscall CCareer__Unk_00420cd0(void *this,int param_1,int param_2)

{
  if (param_1 == -1) {
    return (int)this + *(int *)((int)this + 0x32e40) * 0x516c + 4;
  }
  return (int)this + param_1 * 0x516c + 4;
}
