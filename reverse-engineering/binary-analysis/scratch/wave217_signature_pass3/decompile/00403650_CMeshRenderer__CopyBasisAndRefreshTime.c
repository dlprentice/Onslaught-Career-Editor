/* address: 0x00403650 */
/* name: CMeshRenderer__CopyBasisAndRefreshTime */
/* signature: void __thiscall CMeshRenderer__CopyBasisAndRefreshTime(void * this, void * src_basis, void * dst_basis) */


void __thiscall CMeshRenderer__CopyBasisAndRefreshTime(void *this,void *src_basis,void *dst_basis)

{
  *(undefined4 *)this = *(undefined4 *)src_basis;
  *(undefined4 *)((int)this + 4) = *(undefined4 *)((int)src_basis + 4);
  *(undefined4 *)((int)this + 8) = *(undefined4 *)((int)src_basis + 8);
  *(undefined4 *)((int)this + 0xc) = *(undefined4 *)((int)src_basis + 0xc);
  if (*(int *)((int)this + 0xac) != -0x40800000) {
    *(undefined4 *)((int)this + 0xac) = DAT_00672fd0;
  }
  return;
}
