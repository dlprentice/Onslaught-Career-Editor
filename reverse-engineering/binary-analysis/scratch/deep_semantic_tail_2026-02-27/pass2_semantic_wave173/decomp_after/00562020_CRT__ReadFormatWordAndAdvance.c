/* address: 0x00562020 */
/* name: CRT__ReadFormatWordAndAdvance */
/* signature: int __cdecl CRT__ReadFormatWordAndAdvance(void * param_1) */


int __cdecl CRT__ReadFormatWordAndAdvance(void *param_1)

{
  *(int *)param_1 = *(int *)param_1 + 4;
  return CONCAT22((short)((uint)*(int *)param_1 >> 0x10),*(undefined2 *)(*(int *)param_1 + -4));
}
