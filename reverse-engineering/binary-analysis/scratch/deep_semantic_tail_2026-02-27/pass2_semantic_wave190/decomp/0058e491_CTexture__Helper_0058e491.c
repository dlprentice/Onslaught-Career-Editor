/* address: 0x0058e491 */
/* name: CTexture__Helper_0058e491 */
/* signature: int __thiscall CTexture__Helper_0058e491(void * this, int param_1, int param_2) */


int __thiscall CTexture__Helper_0058e491(void *this,int param_1,int param_2)

{
  int iVar1;
  int unaff_ESI;

  iVar1 = CTexture__Helper_0058e413(this,1,unaff_ESI);
  if (-1 < iVar1) {
    *(int *)(*(int *)((int)this + 0x58) + *(int *)((int)this + 0x5c) * 4) = param_1;
    *(int *)((int)this + 0x5c) = *(int *)((int)this + 0x5c) + 1;
    iVar1 = 0;
  }
  return iVar1;
}
