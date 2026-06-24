/* address: 0x004885e0 */
/* name: CVBufTexture__SetTextureStageFilterByFlag200 */
/* signature: void __thiscall CVBufTexture__SetTextureStageFilterByFlag200(void * this, int param_1, int param_2) */


void __thiscall CVBufTexture__SetTextureStageFilterByFlag200(void *this,int param_1,int param_2)

{
  int *piVar1;

  piVar1 = *(int **)((int)this + 8);
  if ((*(uint *)((int)this + 0x10) & 0x200) == 0x200) {
    (**(code **)(*piVar1 + 0x2c))(piVar1,0,0,param_1,0x2800);
    return;
  }
  (**(code **)(*piVar1 + 0x2c))(piVar1,0,0,param_1,0x800);
  return;
}
