/* address: 0x00491da0 */
/* name: CMapWho__Unk_00491da0 */
/* signature: int __stdcall CMapWho__Unk_00491da0(void * param_1) */


int CMapWho__Unk_00491da0(void *param_1)

{
  int iVar1;

  iVar1 = *(int *)((int)param_1 + 4);
  if ((((-1 < iVar1) && (iVar1 < 5)) && (-1 < *(short *)param_1)) &&
     (((iVar1 = 0x40 >> (4U - (char)iVar1 & 0x1f), *(short *)param_1 < iVar1 &&
       (-1 < *(short *)((int)param_1 + 2))) && (*(short *)((int)param_1 + 2) < iVar1)))) {
    return 1;
  }
  return 0;
}
