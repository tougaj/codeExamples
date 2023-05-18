export interface IGridDayData {
	date: string;
	count?: number;
}

export const rotateArrayLeft = <T extends unknown>([first, ...rest]: T[]) => [...rest, first];
