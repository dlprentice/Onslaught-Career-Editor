/* address: 0x00589846 */
/* name: CTexture__GetCurrentSourceLocation */
/* signature: int __thiscall CTexture__GetCurrentSourceLocation(void * this, int param_1, void * param_2, void * param_3) */


int __thiscall
CTexture__GetCurrentSourceLocation(void *this,int param_1,void *param_2,void *param_3)

{
  if (param_1 != 0) {
    *(undefined4 *)param_1 = *(undefined4 *)(*(int *)((int)this + 0x54) + 0x18);
  }
  if (param_2 != (void *)0x0) {
    *(undefined4 *)param_2 = *(undefined4 *)(*(int *)((int)this + 0x54) + 0x1c);
  }
  return 0;
}
