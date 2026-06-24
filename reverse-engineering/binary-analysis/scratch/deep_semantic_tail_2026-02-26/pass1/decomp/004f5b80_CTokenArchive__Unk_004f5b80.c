/* address: 0x004f5b80 */
/* name: CTokenArchive__Unk_004f5b80 */
/* signature: void __thiscall CTokenArchive__Unk_004f5b80(void * this, int param_1, int param_2, int param_3, void * param_4) */


void __thiscall
CTokenArchive__Unk_004f5b80(void *this,int param_1,int param_2,int param_3,void *param_4)

{
  *(int *)param_3 = param_1;
  *(int *)((int)this + param_2 * 4 + 0xc) = param_3 + 4;
  return;
}
