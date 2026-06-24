/* address: 0x00403650 */
/* name: CMeshRenderer__CopyBasisAndRefreshTime */
/* signature: void __thiscall CMeshRenderer__CopyBasisAndRefreshTime(void * this, void * param_1, void * param_2) */


void __thiscall CMeshRenderer__CopyBasisAndRefreshTime(void *this,void *param_1,void *param_2)

{
  *(undefined4 *)this = *(undefined4 *)param_1;
  *(undefined4 *)((int)this + 4) = *(undefined4 *)((int)param_1 + 4);
  *(undefined4 *)((int)this + 8) = *(undefined4 *)((int)param_1 + 8);
  *(undefined4 *)((int)this + 0xc) = *(undefined4 *)((int)param_1 + 0xc);
  if (*(int *)((int)this + 0xac) != -0x40800000) {
    *(undefined4 *)((int)this + 0xac) = DAT_00672fd0;
  }
  return;
}
