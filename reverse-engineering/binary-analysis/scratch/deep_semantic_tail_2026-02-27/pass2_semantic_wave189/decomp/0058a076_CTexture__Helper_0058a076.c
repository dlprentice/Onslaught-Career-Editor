/* address: 0x0058a076 */
/* name: CTexture__Helper_0058a076 */
/* signature: int __fastcall CTexture__Helper_0058a076(int param_1) */


int __fastcall CTexture__Helper_0058a076(int param_1)

{
  void *this;
  int unaff_ESI;

  this = *(void **)(*(int *)(param_1 + 0x50) + 0x38);
  if (this == (void *)0x0) {
    CTexture__Helper_0058c893((void *)(param_1 + 4),param_1 + 0x60,0x5e6,0x5ea4ac);
    *(undefined4 *)(param_1 + 0x2c) = 1;
    return -0x7fffbffb;
  }
  *(undefined4 *)(param_1 + 0x3c) = *(undefined4 *)((int)this + 4);
  *(undefined4 *)(*(int *)(param_1 + 0x50) + 0x38) = *(undefined4 *)((int)this + 0xc);
  *(undefined4 *)((int)this + 0xc) = 0;
  CTexture__IncludeNodeChain_scalar_deleting_dtor(this,(void *)0x1,unaff_ESI);
  return 0;
}
